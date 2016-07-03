import json

import requests
from bs4 import BeautifulSoup as bs

from .base import BaseParser
from ..point import Point
from ..connection import Connection

from urllib.parse import urlparse, parse_qs

import regex

import asyncio
import aiohttp


RE_BUILDING_NUMBER = regex.compile(r'^(?P<house_number>\d+),?(?P<delimiter>([-/\s]*| (к|К)\.[ ]?))()()(?P<building>\w+)$', regex.UNICODE)
RE_BUILD_NUMBER_NICE_FORMAT = regex.compile()


def is_for_artificial_person(house_str):
    s = house_str.lower()
    return "юр. лица" in s or "юридические лица" in s


def split_house_list(connection):
    if "," in connection.house:
        result = []
        houses = connection.house.split(",")
        for house in houses:
            if house == '':
                continue
            new_c = Connection(provider=connection.provider,
                               region=connection.region,
                               city=connection.city,
                               street=connection.street,
                               house=house.strip(),
                               status=connection.status)
            result.append(new_c)
        return result
    return [connection]


def valid_connection(connection):

    if str(connection.house).isdecimal():
        return [connection]

    match = RE_BUILDING_NUMBER.match(connection.house)
    if match:
        house = connection.house

        new_house = "{} (корпус {})".format(match.groupdict()['house_number'], match.groupdict()['building'])
        new_c = Connection(provider=connection.provider,
                           region=connection.region,
                           city=connection.city,
                           street=connection.street,
                           house=new_house,
                           status=connection.status)
        return [new_c]

    if is_for_artificial_person(connection.house):
        house = connection.house
        house = house.replace("(юридические лица)", "")
        house = house.replace("ЮР. ЛИЦА", "")
        house = house.replace("юр. лица", "")
        status = connection.status + " (юридические лица)"
        new_c = Connection(provider=connection.provider,
                           region=connection.region,
                           city=connection.city,
                           street=connection.street,
                           house=house.strip(),
                           status=status)
        return [new_c]
    if "," in connection.house:
        result = []
        houses = connection.house.split(",")
        for house in houses:
            new_c = Connection(provider=connection.provider,
                               region=connection.region,
                               city=connection.city,
                               street=connection.street,
                               house=house.strip(),
                               status=connection.status)
            result.append(new_c)
        return result
    return [connection]

async def fetch(session, url):
    async with session.get(url) as response:
        if str(response.status) != '200':
            print("Error occured on url {}: {}".format(response.url, response.status))
            return
        return await response.text()

async def fetch_all(session, urls, loop):
    results = await asyncio.gather(
        *[fetch(session, url) for url in urls],
        return_exceptions=True  # default is false, that would raise
    )
    return results


class ByflyParser(BaseParser):
    PARSER_NAME = "byfly"
    PARSER_URL = "http://byfly.by{}"
    BYFLY_MAP_URL = "http://byfly.by/karta-x-pon"
    XPON_CHECK_URL = (
        "http://www.byfly.by/gPON-spisok-domov?page={}&field_obl_x_value_many_to_one={}&field_street_x_value={}&"
        "field_ulica_x_value={}&field_number_x_value={}&field_sostoynie_x_value_many_to_one=All"
    )

    PAGE_STATEMENT = '0,0,0,0,0,0,0,0,0,0,{}'

    REGIONS_MAP = {
        u"all": "All",
        u"брестская": "0",
        u"витебская": "1",
        u"гомельская": "2",
        u"гродненская": "3",
        u"минская": "4",
        u"могилевская": "5",
        u"минск": "6"
    }

    XPON_COME_SOON = u"Переключение на технологию xPON планируется в ближайшее время"
    XPON_AVAILABLE = u"Техническая возможность подключения по технологии xPON имеется"

    FIELD_CLASS_MAP = {
        "provider": "byfly",
        "region": "views-field-field-obl-x-value",
        "city": "views-field views-field-field-street-x-value",
        "street": "views-field-field-ulica-x-value",
        "number": "views-field-field-number-x-value",
        "status": "views-field-field-sostoynie-x-value",
    }

    MAP_SCRIPT_INDEX = 16

    def __init__(self, *args, **kwargs):
        pass

    def get_points(self):
        r = requests.get(self.BYFLY_MAP_URL)
        soup = bs(r.text, "html.parser")
        map_script = soup.find_all("script")[self.MAP_SCRIPT_INDEX]
        clean_script_str = self.__clean_script_str(map_script.text)

        clean_json_str = unescape_text(clean_script_str)

        map_dict = json.loads(clean_json_str)

        points = [Point(m["longitude"], m["latitude"], "")
                  for m in map_dict["gmap"]["auto1map"]["markers"]]
        return points

    def get_connections(self, region="all", city="", street="", house_number=""):
        region = region.lower()
        result = []
        links = self._get_pagination_pages_links(region=region, city=city,
                                                 street_name=street,
                                                 number=house_number)
        links = list(links)
        loop = asyncio.get_event_loop()

        responce_contents = []
        with aiohttp.ClientSession(loop=loop) as session:
            responce_contents = loop.run_until_complete(fetch_all(session, links, loop))

        for r in responce_contents:
            if not r:
                continue
            for c in self._connections_from_page(r):
                result.extend(c)
        return result

    def _get_pagination_pages_links(self, region, city,
                                    street_name, number):
        default_link = self.XPON_CHECK_URL.format(self.PAGE_STATEMENT.format('0'),
                                                  self.REGIONS_MAP[region],
                                                  city,
                                                  street_name,
                                                  number)

        r = requests.get(default_link)
        soup = bs(r.text, "html.parser")
        last_page_link = soup.find("a", title=u"На последнюю страницу", href=True)
        if not last_page_link:
            return [default_link]
        args = parse_qs(urlparse(last_page_link['href']).query)
        page_args = args['page'][0]
        page_count = [i for i in page_args.split(',') if i.isdigit() and int(i)]
        page_count = int(str(page_count[0])) + 1
        pages_links = (self.XPON_CHECK_URL.format(self.PAGE_STATEMENT.format(str(i)),
                                                  self.REGIONS_MAP[region],
                                                  city,
                                                  street_name,
                                                  number)
                       for i in range(page_count))
        return pages_links

    def _connections_from_page(self, page_text):
        soup = bs(page_text, "html.parser")
        rows = soup.find_all("tr", class_=regex.compile(r"(odd|even)"))
        for r in rows:
            yield from self._street_connection_data(r)

    def _street_connection_data(self, street_row):
        status_data = Connection(self.FIELD_CLASS_MAP["provider"],
                                 street_row.find("td", class_=self.FIELD_CLASS_MAP["region"]).text.strip(),
                                 street_row.find("td", class_=self.FIELD_CLASS_MAP["city"]).text.strip(),
                                 street_row.find("td", class_=self.FIELD_CLASS_MAP["street"]).text.strip(),
                                 street_row.find("td", class_=self.FIELD_CLASS_MAP["number"]).text.strip(),
                                 street_row.find("td", class_=self.FIELD_CLASS_MAP["status"]).text.strip())
        return map(valid_connection, split_house_list(status_data))

    def __clean_script_str(self, s):
        res = s.replace('<!--//--><![CDATA[//><!--', '')\
            .replace('//--><!]]>', '')
        res = res.replace('jQuery.extend(Drupal.settings, ', '')
        res = res[:-4]
        return res


def unescape_text(text):
    unescaped = text.replace(r"\x3c", "<").replace(r"\x3e", ">")
    unescaped = unescaped.replace(r"\x3d", "=")
    unescaped = unescaped.replace(r"\x26quot;", "&")
    return unescaped


def main():
    parser = ByflyParser()
    # points = parser.get_points()
    connections = parser.get_connections()
    for c in connections:
        print(c)
    # print(points)


if __name__ == '__main__':
    main()
