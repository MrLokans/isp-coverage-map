import json

import requests
from bs4 import BeautifulSoup as bs

from .base import BaseParser


class ADSL_Parser(BaseParser):
    PARSER_NAME = "ADSL"
    PARSER_URL = "https://adsl.by"
    SEARCH_URL = "https://adsl.by/connection/ethernet/autocomplete/"
    CONNECTION_URL = "https://adsl.by/connection?connection=ethernet"
    HOUSE_URL = "https://adsl.by/connection/js/check"

    def _get_streets(self):
        letters = "0123456789абвгдеёжзийклмнопрстуфхцчшщэюя"
        streets = set()
        for l in letters:
            u = "/".join([self.SEARCH_URL, l])
            for k in requests.get(u).json():
                streets.add(k)
        return streets

    def get_connections(self):
        streets = self._get_streets()
        print(streets)
        return []

    def _get_form_build_id(self):
        """Get form_build_id param value to make correct XHR requests"""
        page_content = requests.get(self.CONNECTION_URL).text
        soup = bs(page_content, "html.parser")
        selected = soup.select("form.connection-form input[name=\"form_build_id\"]")
        print(selected)
        _id = selected[0]["value"]
        return _id

    def _house_list_for_street(self, street, houses=None):
        if not getattr(self, "form_id", None):
            self.form_id = self._get_form_build_id()
        if houses is None:
            houses = list(range(120))
        for n in houses:
            data = {
                "type_connection": "ethernet",
                "street": "улица Матусевича",
                "number_house": str(n),
                "form_id": "connection_request",
                "form_build_id": self.form_id,
                "button-check": "Проверить",
                "disabled_next_step": "1",
                "h_case": ""
            }
            r = requests.post(self.HOUSE_URL, data=data)
            text = r.text.replace('\\\\', '\\')
            text = text.replace('\\x3c', '<')
            text = text.replace('\\x3e', '>')
            text = text.replace('\\x26', '&')
            text = text.replace("\\'", "'")
            json_data = json.loads(text)
            soup = bs(json_data['data'], "html.parser")
            result = soup.find("div", {"id": "connection-body-result"})
            print(result)

    def get_points(self):
        return []

if __name__ == '__main__':
    parser = ADSL_Parser(None)
    # for c in parser.get_connections():
    #     print(c)
    parser._house_list_for_street("")
