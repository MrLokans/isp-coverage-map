import csv


class CSV_Exporter(object):
    @staticmethod
    def export_points(filename, points):
        with open(filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["longitude", "latitude", "description"])
            for point in points:
                writer.writerow([point.longitude,
                                 point.latitude,
                                 point.description])
