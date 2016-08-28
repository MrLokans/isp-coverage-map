import abc
import logging

import redis

logger = logging.getLogger(__name__)


class AbstractCache(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_coordinate(street_name, house_number):
        """Returns (longitude, latitude) tuple from cache"""
        pass

    @abc.abstractmethod
    def put_coordinate(street_name, house_number):
        """Puts coordinate into cache cache"""
        pass


class RedisCache(AbstractCache):
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
            put = self._connection.set(key, value)
            if not put:
                err_msg = "Item {}-{} was not cached for some reason."
                logger.error(err_msg.format(key, value))
        except redis.exceptions.ConnectionError:
            err_msg = "Error putting key {} with value {} into cache."
            logger.error(err_msg.format(key, value), exc_info=True)