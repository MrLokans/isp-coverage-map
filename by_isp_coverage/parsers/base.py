import abc


class BaseParser(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_points(self):
        pass

    @abc.abstractmethod
    def get_connections(self, city="", street="", house_number=""):
        return []
