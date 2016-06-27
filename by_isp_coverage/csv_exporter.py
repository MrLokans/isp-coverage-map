import csv

from .connection import Connection
from .point import Point


class CSV_Exporter(object):

    @classmethod
    def export_namedtuple_values(cls, filename, data, tpl_cls):
        assert hasattr(tpl_cls, "_fields")
        with open(filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(tpl_cls._fields)
            for elem in data:
                writer.writerow([getattr(elem, f) for f in tpl_cls._fields])

    @classmethod
    def export_points(cls, filename, points):
        cls.export_namedtuple_values(filename, points, Point)

    @classmethod
    def export_connections(cls, filename, connections):
        cls.export_namedtuple_values(filename, connections, Connection)
