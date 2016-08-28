import json
import logging
import queue

import requests
from bs4 import BeautifulSoup as bs

from by_isp_coverage.parsers.base import BaseParser
from by_isp_coverage.point import Point
from by_isp_coverage.connection import Connection

from urllib.parse import urlparse, parse_qs

import regex

import asyncio
import aiohttp

# Just empirically chosen, no benchmarks were made
MAX_NUMBER_OF_CONCURRENT_CONNECTIONS = 4

logger = logging.getLogger("parsers.byfly_parser")

async def fetch(session, url, sem, error_queue):
    with (await sem):
        async with session.get(url) as response:
            if str(response.status) != '200':
                print("Error occured on url {}: {}, putting in the error queue".format(response.url, response.status))
                error_queue.put(url)
                return
            return await response.text()

async def fetch_all(session, urls, loop):
    sem = asyncio.Semaphore(MAX_NUMBER_OF_CONCURRENT_CONNECTIONS)
    error_queue = queue.Queue()
    results = await asyncio.gather(
        *[fetch(session, url, sem, error_queue) for url in urls],
        return_exceptions=True  # default is false, that would raise
    )
    return results, error_queue


class ByflyParser(BaseParser):
    PARSER_NAME = "byfly"
    PARSER_URL = "http://byfly.by"
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

    def __init__(self, *args, validator=None, **kwargs):
        self.validator = validator

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

    def get_connections(self, region="all", city="",
                        street="", house_number=""):
        region = region.lower()

        links = self._get_pagination_pages_links(region=region, city=city,
                                                 street_name=street,
                                                 number=house_number)
        links = list(links)
        loop = asyncio.get_event_loop()

        response_contents = []
        with aiohttp.ClientSession(loop=loop) as session:
            response_contents, error_queue = loop.run_until_complete(fetch_all(session, links, loop))

        # Syncronously obtain data from error urls
        while not error_queue.empty():
            try:
                u = error_queue.get()
                response_contents.append(requests.get(u)).text
            except Exception as e:
                logger.exception("Error parsing url: {}".format(u))

        for page_content in response_contents:
            if not page_content:
                continue

            connections = self._connections_from_page(page_content)
            if self.validator:
                yield from self.validator.validate_connections(connections)
            else:
                yield from connections

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
        page_count = [i for i in page_args.split(',')
                      if i.isdigit() and int(i)]
        page_count = int(str(page_count[0])) + 1
        pages_links = (self.XPON_CHECK_URL.format(self.PAGE_STATEMENT.format(str(i)),
                                                  self.REGIONS_MAP[region],
                                                  city,
                                                  street_name,
                                                  number)
                       for i in range(page_count))
        return pages_links

    def _connections_from_page(self, page_text: str):
        soup = bs(page_text, "html.parser")
        rows = soup.find_all("tr", class_=regex.compile(r"(odd|even)"))
        for r in rows:
            yield self._connection_from_row(r)

    def _row_connection_components(self, row: bs):
        def get_td_elem(field_name):
            result = row.find("td", class_=self.FIELD_CLASS_MAP[field_name])
            return result
        search_fields = ("region", "city", "street", "number", "status")
        return (get_td_elem(field_name).text.strip()
                for field_name in search_fields)

    def _connection_from_row(self, row):
        connection = Connection(self.PARSER_NAME,
                                *self._row_connection_components(row))
        return connection

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

if __name__ == '__main__':
    main()
