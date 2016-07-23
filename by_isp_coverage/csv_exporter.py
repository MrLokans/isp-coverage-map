import csv
from inspect import isgenerator

from .connection import Connection
from .point import Point


class CSV_Exporter(object):

    @classmethod
    def export_namedtuple_values(cls, filename, data):
        with open(filename, "w") as f:
            cls._export_namedtuple_values_fd(f, data)

    @classmethod
    def _export_namedtuple_values_fd(cls, fd, class_sequence):
        if isgenerator(class_sequence):
            first_elem = next(class_sequence)
        else:
            first_elem = class_sequence[0]
            class_sequence = class_sequence[1:]
        assert hasattr(first_elem, "_fields")
        writer = csv.writer(fd)
        writer.writerow(first_elem._fields)
        writer.writerow([getattr(first_elem, f) for f in first_elem._fields])
        for elem in class_sequence:
            writer.writerow([getattr(elem, f) for f in elem._fields])

    @classmethod
    def export_points(cls, filename, points):
        cls.export_namedtuple_values(filename, points)

    @classmethod
    def export_connections(cls, filename, connections):
        cls.export_namedtuple_values(filename, connections)
