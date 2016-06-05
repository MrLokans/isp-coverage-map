import re
import json
from queue import Queue

from geopy.geocoders import GoogleV3

from lxml.html import fromstring
import grequests

from point import Point


STREET_ID_REGEX = r"this,\"(?P<_id>\d+)\""


class UNETParser(object):
    PARSER_NAME = "UNET"
    BASE_URL = "http://unet.by"

    def street_names_from_json(self, json_file):
        streets = []
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
            streets = [s["name"] for s in data["items"]]
            streets = [self._update_street_name(s) for s in streets]
        return streets

    def _update_street_name(self, street_name):
        """Moves words like 'street', 'crs' to the end of the name"""
        splitted = street_name.split(" ")
        if len(splitted) > 0 and splitted[0] == 'улица':
            splitted.pop(0)
        return " ".join(splitted)

    def houses_with_connection_on_street(self, street):
        """Gets all house numbers if any on the street"""
        u = self.BASE_URL
        street_id, _ = street
        nmbrs = range(1, 10)
        houses = []
        rs = (grequests.get(u, params={"act": "get_street_data",
                                       "data": n,
                                       "street": street_id})
              for n in nmbrs)
        results = grequests.map(rs)
        for resp in results:
            houses.extend(self._houses_from_api_response(resp))
        return houses

    def get_all_connected_streets(self):
        ltrs = "0123456789абвгдеёжзийклмнопрстуфхцчшщэюя"
        u = self.BASE_URL

        streets = []
        rs = (grequests.get(u, params={"act": "get_street", "data": l})
              for l in ltrs)
        results = grequests.map(rs)
        for response in results:
            streets.extend(self._streets_from_api_response(response))
        streets = list(filter(lambda x: bool(x[1]), streets))
        return streets

    def _streets_from_api_response(self, resp):
        text = resp.text
        if not text:
            return ""
        results = []
        tree = fromstring(text)
        links = tree.xpath('//a')
        for link in links:
            link_text = link.text.strip()
            onclick = link.get('onclick')
            _id = re.search(STREET_ID_REGEX, onclick).groupdict()['_id']
            results.append((_id, link_text))
        return results

    def _houses_from_api_response(self, resp):
        text = resp.text
        if not text:
            return ""
        tree = fromstring(text)
        links = tree.xpath('//a/text()')
        return links

    def get_points(self, json_file=None):
        geolocator = GoogleV3()

        to_process = Queue()
        results = Queue()

        with open("results.txt", "w", encoding="utf-8") as f:
            points = []
            data = {}
            # If no file specified we grab all the data from the web site
            if json_file is None:
                print("Collecting streets.")
                streets = self.get_all_connected_streets()
                print("Collecting house numbers.")
                houses = [{s[1]: self.houses_with_connection_on_street(s)}
                          for s in streets]
                with open("unet_output.json", "w", encoding="utf-8") as fp:
                    data = {"houses": houses}
                    json.dump(data, fp)
            # Otherwise use existing
            data = json.load(open(json_file, encoding="utf-8"))
            pass
            city = "Минск"
            for street in data["houses"]:
                name = list(street.keys())[0]
                houses = street[name]
                for house in houses:
                    search_str = " ".join([city, name, house])
                    to_process.put(search_str)
            while True:
                # It's better to use threading later
                search_str = to_process.get()
                if search_str is None:
                    break
                print("Looking for {}".format(search_str))
                location = geolocator.geocode(search_str)
                point = Point(longitude=location.longitude,
                              latitude=location.latitude,
                              description="")
                # Caching results in file
                f.write(str(point) + "\n")
                points.append(point)
            return points

if __name__ == '__main__':
    parser = UNETParser()
    parser.get_points()
    # parser.get_points(json_file="unet_output.json")
