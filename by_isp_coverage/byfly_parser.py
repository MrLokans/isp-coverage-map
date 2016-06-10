import json

import requests
from bs4 import BeautifulSoup as bs

from .base import BaseParser
from .point import Point


class ByflyParser(BaseParser):
    PARSER_NAME = "byfly"
    BYFLY_MAP_URL = "http://byfly.by/karta-x-pon"
    MAP_SCRIPT_INDEX = 16

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
    points = parser.get_points()
    print(points)


if __name__ == '__main__':
    main()
