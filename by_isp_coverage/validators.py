from typing import Iterable

import regex
from collections import abc

from .connection import Connection

CITY_PARTS_TO_EXCLUDE = ("д.г.п.", "п.г.т", "аг.", "г.п.", "агр.",
                         "д.", "г.", "п.", "к.")

# reference article: http://bit.ly/2aDXXAd
RE_HOUSE_NUMBER = regex.compile(r'''^\d+ # Digital house number
                                    (?P<splitter>[-\/])? # optional splitter
                                    (?(splitter) # if splitter group exists
                                        (\d+|[А-Яа-я]+) # after it should be digits or letters
                                            |  # otherwise
                                        [А-Яа-я]?) # only letters
                                ''', regex.UNICODE | regex.X)

BUILDING_NUM_RE_STR = r'''^(?P<house_number>\d+(?P<splitter>[-\/])?(?(splitter)(\d+|[А-Яа-я]+)|[А-Яа-я]?))  # see explanation above
                          ,?\s*  # Possible splitters
                          (корпус|корп\.|к\.|к) # building number identifier
                          \s? # Possible splitter
                          (?P<building>[\d]+) # Actual decimal building number
                        '''

RE_BUILDING_NUMBER = regex.compile(BUILDING_NUM_RE_STR,
                                   regex.UNICODE | regex.X)


def is_for_artificial_person(house_str):
    s = house_str.lower()
    return "юр. лица" in s or "юридические лица" in s


class ConnectionValidator(object):
    def __init__(self, fields=None,
                 pre_replacement_street_map=None,
                 post_replacement_street_map=None):
        """
        :param fields: list of field names to be validated
        """
        self.fields = fields if fields else ("house", "provider", "region",
                                             "city", "street", "status")
        self.pre_replacement_street_map = pre_replacement_street_map\
                                          if pre_replacement_street_map\
                                          else {}
        self.post_replacement_street_map = post_replacement_street_map\
                                           if post_replacement_street_map\
                                           else {}

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
        It looks for method _validate_{field}_field
        defined in the validator class and calls it against
        every connection object.
        Validation method returns sequence of validated field values
        and, if required, callbacks that may mutate original connection object.

        Note that each of validators should return a list of fields instead
        of a single validated field value.

        :param connections: Sequence of connections to be validated
        :param field: string, name of the field to be validated
        :return: new sequence of validated connection objects
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
            new_house = "{} (корпус {})".format(d['house_number'].upper(),
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
        if RE_HOUSE_NUMBER.match(house):
            return [house.upper().replace(' ', '')]
        return [house]

    def validate_status_field(self, status):
        return [status]

    def validate_region_field(self, region):
        return [region]

    def validate_provider_field(self, provider):
        return [provider]

    def validate_street_field(self, street):
        t = Toponym(street,
                    default_type="улица",
                    pre_replacement=self.pre_replacement_street_map,
                    post_replacement=self.post_replacement_street_map)
        return [t.format()]


class Toponym(object):
    """This class handles toponyms
    parsing and formatting"""

    SUPPORTED_TYPES = ('улица', 'переулок', 'проспект', 'проезд',
                       'бульвар', 'микрорайон')
    PRE_VALIDATORS = {
        "3ий пер Волчецкого": ("переулок", "3-й Волчецкого"),
        "А/Г ЛЕСНОЙ АЛЕКСАНДРОВА УЛ.": ("улица", "Александрова (агрогородок Лесной)"),
    }

    POST_VALIDATORS = {
        "9Мая": "9 Мая",
        "Б.Хмельницкого": "Богдана Хмельницкого",
        "Б. Хмельницкого": "Богдана Хмельницкого",
        "К. Маркса": "Карла Маркса",
        "К.Маркса": "Карла Маркса",
        "К.Либкнехта": "Карла Либкнехта",
        "К. Либкнехта": "Карла Либкнехта",
        "Я. Колоса": "Якуба Колоса",
        "Я.Колоса": "Якуба Колоса",
        "Я.Купалы": "Янки Купалы",
        "Я. Купалы": "Янки Купалы",
    }
    TYPE_MAP = (
        (regex.compile(r"(прз\.|пр\-д|проезд)", regex.IGNORECASE), "проезд"),
        (regex.compile(r"(пос\.|поселок)", regex.IGNORECASE), "поселок"),
        (regex.compile(r"(мр\-н|микрорайон)", regex.IGNORECASE), "микрорайон"),
        (regex.compile(r"(а\/г)", regex.IGNORECASE), "агрогородок"),
        (regex.compile(r"(переулок|пер\.)", regex.IGNORECASE), "переулок"),
        (regex.compile(r"(б\-р|бул\.|бульвар)", regex.IGNORECASE), "бульвар"),
        (regex.compile(r"(ул\,|\, ул\.|\, ул|ул\.|улица)",
                       regex.IGNORECASE), "улица"),
        (regex.compile(r"(проспект|пр-кт|пр-т|пр\.)",
                       regex.IGNORECASE), "проспект"),
    )

    def __init__(self, s, default_type="улица",
                 pre_replacement=None,
                 post_replacement=None):
        """
        Builds new toponym object from string
        :param s: string to build toponym from (e.g. 'ул. Красноармейская')
        :param default_type: default type to be used if
        it is not possible to correctly parse name
        :param post_replacement: mapping of toponyms names that should be
        manually replaced after performing all of validations.
        :type default_type: str or unicode
        :type s: str or unicode
        """
        self._original_str = s
        self._default_type = default_type
        if pre_replacement and isinstance(pre_replacement, abc.Mapping):
            self.PRE_VALIDATORS.update(pre_replacement)
        if post_replacement and isinstance(post_replacement, abc.Mapping):
            self.POST_VALIDATORS.update(post_replacement)
        self.tokenize(s)
        self.post_validate()

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def tokenize(self, name):
        """
        Splits toponym into correct type and name,
        if impossible - throws ToponymParsingError
        """
        if name in self.PRE_VALIDATORS:
            """If toponym name is found in pre_replacement_map all
            validations are skipped and the value is replaced taken
            from the map
            """
            self._type, self._name = self.PRE_VALIDATORS[name]
            return
        _type, name = self._extract_type_and_name(name)
        if _type is None:
            _type = self._default_type
        self._type, self._name = _type, self._normalize_name(name)

    def format(self, format=""):
        """Formats toponym's name.
        Currently it only uses default implementation
        """
        # TODO: add formatting strings support
        return "{type} {name}".format(type=self.type, name=self.name)

    def _extract_type_and_name(self, name):
        for type_regex, type_value in self.TYPE_MAP:
            match = type_regex.search(name)
            if match:
                new_name = name.replace(name[match.start():match.end()], "")
                return type_value, new_name.strip()
        return None, name.strip()

    @classmethod
    def _normalize_name(self, name, ignored=None):
        """
        Change case of letters in the street name to an
        appropriate format.
        """
        return name.title()

    def post_validate(self):
        """
        Some entries have to be updated manually
        (e.g. К.Маркса should be turned into Карла Маркса), this
        method runs those manual validations
        """
        if self._name in self.POST_VALIDATORS:
            self._name = self.POST_VALIDATORS[self._name]
