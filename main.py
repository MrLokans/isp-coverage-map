from byfly_parser import ByflyParser
from mts_parser import MTS_Parser

from csv_exporter import CSV_Exporter


def main():
    byfly_parser = ByflyParser()
    mts_parser = MTS_Parser()

    exporter = CSV_Exporter()

    for parser in [byfly_parser, mts_parser]:
        output_name = parser.PARSER_NAME + ".csv"
        dots = parser.get_points()
        exporter.export_points(output_name, dots)


if __name__ == '__main__':
    main()
