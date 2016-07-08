import regex

from .connection import Connection

CITY_PARTS_TO_EXCLUDE = ("д.г.п.", "п.г.т", "аг.", "г.п.", "агр.",
                         "д.", "г.", "п.", "к.")

RE_BUILDING_NUMBER = regex.compile(r'^(?P<house_number>\d+),?(?P<delimiter>([-/\s]*| (к|К)\.[ ]?))()()(?P<building>\w+)$', regex.UNICODE)


def is_for_artificial_person(house_str):
    s = house_str.lower()
    return "юр. лица" in s or "юридические лица" in s


def split_house_list(connection):
    if "," in connection.house:
        result = []
        houses = connection.house.split(",")
        for house in houses:
            if house == '':
                continue
            new_c = Connection.from_modified_connection(connection,
                                                        house=house.strip())
            result.append(new_c)
        return result
    return [connection]


class ConnectionValidator(object):
    def __init__(self, fields=None):
        self.fields = fields if fields else ("provider", "region", "city",
                                             "street", "house", "status")

    def validate_connections(self, connections):
        return self._validate_city(connections)

    def __validate_field(self, connections, field):
        validate_strategy = getattr(self, "validate_{}_field".format(field))
        constructor = Connection.from_modified_connection
        for c in connections:
            fields = (f for f in validate_strategy(getattr(c, field)))
            for f in fields:
                yield constructor(c, **{field: f})

    def _validate_city(self, connections):
        return self.__validate_field(connections, "city")

    def validate_city_field(self, city):
        if city.endswith(" п"):
            city = city.replace(" п", "")

        for part in CITY_PARTS_TO_EXCLUDE:
            if part in city:
                city = city.replace(part, '')
        city = city.lower().title()

        yield city.strip()

    def valid_connection(connection):
        if str(connection.house).isdecimal():
            return [connection]

        match = RE_BUILDING_NUMBER.match(connection.house)
        if match:
            house = connection.house

            new_house = "{} (корпус {})".format(match.groupdict()['house_number'], match.groupdict()['building'])
            new_c = Connection.from_modified_connection(connection,
                                                        house=new_house)
            return [new_c]

        if is_for_artificial_person(connection.house):
            house = connection.house
            house = house.replace("(юридические лица)", "")
            house = house.replace("ЮР. ЛИЦА", "")
            house = house.replace("юр. лица", "")
            status = connection.status + " (юридические лица)"
            new_c = Connection.from_modified_connection(connection,
                                                        house=house.strip(),
                                                        status=status)
            return [new_c]
        if "," in connection.house:
            result = []
            houses = connection.house.split(",")
            for house in houses:
                new_c = Connection.from_modified_connection(connection,
                                                            house=house.strip())
                result.append(new_c)
            return result
        return [connection]
