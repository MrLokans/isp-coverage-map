import abc


class BaseParser(metaclass=abc.ABCMeta):

    def __init__(self, coordinate_obtainer, validator=None):
        self.coordinate_obtainer = coordinate_obtainer
        self.validator = validator

    @abc.abstractmethod
    def get_points(self):
        pass

    @abc.abstractmethod
    def get_connections(self, region="", city="", street="", house_number=""):
        return []
