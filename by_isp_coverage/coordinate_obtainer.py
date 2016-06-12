from queue import Queue

import redis
from geopy.geocoders import Yandex

from .point import Point


class RedisCache(object):
    """This class implements caching interface
    for redis backend"""

    def __init__(self, currency_cls, logger_name):

        prefs = {"host": "localhost",
                 "port": "6379",
                 "db": "geodata"}
        self._connection = redis.StrictRedis(**prefs)

    def get_coordinate(self, street_name, house_number):
        key = "{}-{}".format(street_name, house_number)
        try:
            item = self._connection.get(key)
            if item is None:
                return None
            long, lat = item.split('|')
            return long, lat
        except redis.exceptions.ConnectionError:
            return None
        return None

    def put_coordinate(self, street_name, house_number, long, lat):
        key = "{}-{}".format(street_name, house_number)
        value = "{}|{}".format(long, lat)
        try:
            self._connection.set(key, value)
        except redis.exceptions.ConnectionError:
            pass


class CoordinateObtainer(object):
    def __init__(self, name, street_data,
                 cache_class=RedisCache, locator_class=Yandex):
        # Street data is the list with the following structure:
        # [('Street name', [1, 2, 3, 4]), ...]
        self.name = name
        self.street_data = street_data
        self._cache = cache_class()
        self._locator = locator_class()

    def get_points(self, street_data):
        """Street data has a following structure:
        [("Street name", [1, 4, 5, 9]), ...]
        """

        to_process = Queue()
        processed = Queue()

        # Fill queue with data
        for street_name, houses in street_data:
            for house in houses:
                to_process.put((street_name, house))

        while True:
            if to_process.empty():
                break
            # It's better to use threading later
            house_data = to_process.get()
            if house_data is None:
                break
            street_name, house_number = house_data

            # Lookup in cache
            coord = self._cache.get_coordinate(street_name, house)
            if coord is not None:
                point = Point(longitude=coord[0],
                              latitude=coord[1],
                              description="")
                print("Cached value found: {}".format(point))
                processed.put(point)

            else:
                search_str = " ".join(["Минск", street_name, house_data])
                location = self._locator.geocode(search_str)
                try:
                    point = Point(longitude=location.longitude,
                                  latitude=location.latitude,
                                  description="")
                    processed.put(point)
                except Exception as e:
                    print("While processing {} error occured: {}".format(str(e)))
        results = []
        while not processed.empty():
            results.append(processed.get())
        return results
