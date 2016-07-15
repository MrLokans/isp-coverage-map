from typing import Iterable

import regex

from .connection import Connection

CITY_PARTS_TO_EXCLUDE = ("д.г.п.", "п.г.т", "аг.", "г.п.", "агр.",
                         "д.", "г.", "п.", "к.")

RE_BUILDING_NUMBER = regex.compile(r'^(?P<house_number>\d+),?(?P<delimiter>([-/\s]*| (к|К)\.[ ]?))()()(?P<building>\w+)$', regex.UNICODE)


def is_for_artificial_person(house_str):
    s = house_str.lower()
    return "юр. лица" in s or "юридические лица" in s


class ConnectionValidator(object):
    def __init__(self, fields=None):
        self.fields = fields if fields else ("house", "provider", "region", "city",
                                             "street", "status")

    def validate_connections(self,
                             connections: Iterable[Connection]) -> Iterable[Connection]:
        """Runs a set of validations on the given connections sequence,
        and yield validated connections"""
        for f in self.fields:
            connections = self.__validate_field(connections, f)
        return connections

    def __validate_field(self,
                         connections: Iterable[Connection],
                         field: str) -> Iterable[Connection]:
        """An internal method running validations against the specified field.
        It looks for methods like _validate_{field}_field defined in the validator class
        and calls them on the specified connection field.
        Methods return sequence of validated field values and, if required,
        callbacks that, in their turn mutate original connection object.
        """
        validate_strategy = getattr(self, "validate_{}_field".format(field))
        constructor = Connection.from_modified_connection
        for c in connections:
            field_to_validate = getattr(c, field)
            fields = (f for f in validate_strategy(field_to_validate))
            for f in fields:
                try:
                    callback = f[1]
                    conn = constructor(c, **{field: f[0]})
                    callback(conn)
                    yield conn
                except (IndexError, TypeError):
                    yield constructor(c, **{field: f})

    def _validate_city(self, connections):
        return self.__validate_field(connections, "city")

    def _validate_house(self, connections):
        yield from self.__validate_field(connections, "house")

    def validate_city_field(self, city):
        if city.endswith(" п"):
            city = city.replace(" п", "")

        for part in CITY_PARTS_TO_EXCLUDE:
            if part in city:
                city = city.replace(part, '')
        city = city.lower().title()

        return [city.strip()]

    def validate_house_field(self, house):
        if str(house).isdecimal():
            return [house]
        match = RE_BUILDING_NUMBER.match(house)
        if match:
            d = match.groupdict()
            new_house = "{} (корпус {})".format(d['house_number'],
                                                d['building'])
            return [new_house]
        if is_for_artificial_person(house):
            # We need to mutate original connection
            # status, and we do it via callback
            house = house.replace("(юридические лица)", "")
            house = house.replace("ЮР. ЛИЦА", "")
            house = house.replace("юр. лица", "")

            def status_update_callback(c):
                c.status = c.status + " (юридические лица)"

            return [(house.strip(), status_update_callback)]

        if "," in house:
            house = house.replace(" ", "")
            houses = [h for h in house.split(",") if h != ""]
            return houses
        return [house]

    def validate_status_field(self, status):
        return [status]

    def validate_region_field(self, region):
        return [region]

    def validate_provider_field(self, provider):
        return [provider]

    def validate_street_field(self, street):
        return [street]


class Toponym(object):
    """This class handles toponyms
    parsing and formatting"""

    SUPPORTED_TYPES = ('улица', 'переулок', 'проспект', 'проезд',
                       'бульвар', 'микрорайон')

    # тракт, площадь, шоссе??

    def __init__(self, s, default_type="улица"):
        """
        Builds new toponym object from string
        :param s: string to build toponym from (e.g. 'ул. Красноармейская')
        :param default_type: default type to be used if it is not possible to coeectly parse name
        :type default_type: str or unicode
        :type s: str or unicode
        """
        self._original_str = s
        self._type, self._name = self.tokenize(s)

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    def tokenize(self, s):
        """
        Splits toponym into correct type and name,
        if impossible - throws ToponymParsingError
        """
        return "", ""
