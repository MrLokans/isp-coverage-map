import logging
from queue import Queue

import redis
from geopy.geocoders import Yandex

from .point import Point

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RedisCache(object):
    """This class implements caching interface
    for redis backend"""

    def __init__(self):

        prefs = {"host": "localhost",
                 "port": "6379",
                 "db": "1"}
        self._connection = redis.StrictRedis(**prefs)

    def get_coordinate(self, street_name, house_number):
        key = "{}-{}".format(street_name, house_number)
        try:
            item = self._connection.get(key)
            if item is None:
                return None
            item = item.decode('utf-8')
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
            err_msg = "Error putting key {} with value {} into cache."
            logger.error(err_msg.format(key, value), exc_info=True)


class CoordinateObtainer(object):
    def __init__(self,
                 cache_class=RedisCache, locator_class=Yandex):
        # Street data is the list with the following structure:
        # [('Street name', [1, 2, 3, 4]), ...]
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
                msg = "Cached value found for {} -{}: {}"
                logger.debug(msg.format(street_name, house, point))
                processed.put(point)
            else:
                search_str = " ".join(["Минск", street_name, house_number])
                logger.debug("Getting data about {}".format(search_str))

                try:
                    location = self._locator.geocode(search_str)
                    point = Point(longitude=location.longitude,
                                  latitude=location.latitude,
                                  description="")
                    logger.debug("Putting {} in cache".format(search_str))
                    self._cache.put_coordinate(street_name, house_number,
                                               point.longitude, point.latitude)
                    processed.put(point)
                except Exception:
                    err_msg = "While processing {} error occured"
                    logger.error(err_msg.format(search_str), exc_info=True)
        while not processed.empty():
            yield processed.get()
