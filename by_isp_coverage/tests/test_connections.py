import re
import unittest

from ..connection import Connection


class TestConnectionClass(unittest.TestCase):

    def create_connection(self, provider="test provider",
                          region="test region",
                          city="test city",
                          street="test street",
                          house="test house",
                          status="test status"):
        _locals = locals().copy()
        _locals.pop('self')
        return Connection(**_locals)

    def test_objects_created_normally(self):
        c = self.create_connection()
        self.assertEqual(c.provider, "test provider")
        self.assertEqual(c.region, "test region")
        self.assertEqual(c.city, "test city")
        self.assertEqual(c.street, "test street")
        self.assertEqual(c.house, "test house")
        self.assertEqual(c.status, "test status")

    def test_connection_object_created_from_modified_connection(self):
        c = self.create_connection()
        new_c = Connection.from_modified_connection(c, region="new region",
                                                    city="new city")
        expected_c = self.create_connection(region="new region",
                                            city="new city")
        self.assertEqual(new_c, expected_c)

    def test_connection_object_created_from_modified_connection_and_incorrect_fields(self):
        c = self.create_connection()
        new_c = Connection.from_modified_connection(c, blabla="new region",
                                                    noway="new city")
        expected_c = self.create_connection()
        self.assertEqual(new_c, expected_c)

    def test_dictionary_methods_applicable(self):
        c = self.create_connection()
        self.assertEqual(c["city"], "test city")
        self.assertEqual(c["region"], "test region")
        self.assertEqual(c["status"], "test status")
        self.assertEqual(c["street"], "test street")

    def test_obtaining_not_existent_field_raises_error(self):
        c = self.create_connection()
        with self.assertRaises(KeyError):
            c["unknownattribute"]

if __name__ == '__main__':
    unittest.main()
