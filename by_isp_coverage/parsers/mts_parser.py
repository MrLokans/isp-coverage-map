import re
from collections import defaultdict

import requests

from .base import BaseParser
from ..connection import Connection
from ..point import Point


class MTS_Parser(BaseParser):
    PARSER_NAME = "MTS"
    PARSER_URL = "http://www.mts.by"
    MTS_MAP_URL = "http://www.mts.by/home/connect/"
    YA_MAPS_POINT_REGEX = r"var placemark(?P<id>[\d]+) = new YMaps.Placemark\(new YMaps\.GeoPoint\((?P<long>[\d]+\.[\d]+),(?P<lat>[\d]+\.[\d]+)"
    # Note that we are using non-gready quantifiers (*?)
    YA_MAPS_POINT_NAME_REGEX = r'placemark(?P<id>[\d]+)\.name = "(?P<name>[^\']*?)";'
    YA_MAPS_POINT_DESCRIPTION_REGEX = r'placemark(?P<id>[\d]+)\.description = "(?P<description>[^\']*?)";'

    def __init__(self, *args, **kwargs):
        pass

    def _extract_point_name(self, point_id):
        pass

    def _coordinates_from_map(self, page_content):
        return ((c.groupdict()['long'], c.groupdict()['lat'])
                for c in re.finditer(self.YA_MAPS_POINT_REGEX, page_content))

    def parse_description(self, description):
        address, status = description.split('<BR/>')
        city_comp, street_comp, house_comp = address.split(',')
        city = city_comp.split(":")[1].strip()
        street = street_comp.strip()
        house = house_comp.strip()
        return (city, street, house, status)

    def get_connections(self):
        results = defaultdict(dict)
        r = requests.get(self.MTS_MAP_URL)
        text = r.text.encode('utf-8').decode('utf-8')
        for c in re.finditer(self.YA_MAPS_POINT_NAME_REGEX, text):
            results[c.groupdict()['id']]['name'] = c.groupdict()['name']

        for c in re.finditer(self.YA_MAPS_POINT_DESCRIPTION_REGEX, text):
            id_ = c.groupdict()['id']
            description = c.groupdict()['description']
            city, street, house, status = self.parse_description(description)
            results[id_]['city'] = city
            results[id_]['street'] = street
            results[id_]['house'] = house
            results[id_]['status'] = ". ".join([results[id_]['name'], status])\
                                     .strip()
            del results[id_]['name']
        for k, v in results.items():
            yield Connection("mts", "", v['city'], v['street'],
                             v['house'], v['status'])

    def get_points(self):
        """Parse MTS site and extract points from map"""
        r = requests.get(self.MTS_MAP_URL)
        text = r.text.encode('utf-8').decode('utf-8')
        return (Point(*c, "") for c in self._coordinates_from_map(text))


if __name__ == '__main__':
    parser = MTS_Parser()
    for c in parser.get_connections():
        print(c)
