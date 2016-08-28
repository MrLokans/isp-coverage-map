"""
Contains class responsible for coordinate obtaining
from adress
"""

import logging
from queue import Queue

from geopy.geocoders import Yandex

from by_isp_coverage.point import Point
from by_isp_coverage.cache import RedisCache

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
            coord = self._cache.get_coordinate(street_name, house_number)
            if coord is not None:
                point = Point(longitude=coord[0],
                              latitude=coord[1],
                              description="")
                msg = "Cached value found for {} - {}: {}"
                logger.debug(msg.format(street_name, house_number, point))
                processed.put(point)
            else:
                search_str = " ".join(["Минск", street_name, house_number])

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
