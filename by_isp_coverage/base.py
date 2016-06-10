import abc


class BaseParser(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_points():
        pass
