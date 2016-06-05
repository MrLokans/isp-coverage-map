import argparse

from .byfly_parser import ByflyParser
from .mts_parser import MTS_Parser
from .unet_parser import UNETParser

from .csv_exporter import CSV_Exporter


def parse_args():
    desc = "Get geo data about high-speed internet availability in Minsk and Belarus"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--name", help="Name of parser to use.", required=True)
    parser.add_argument("path", help="name of file (csv) to export data to.")
    args = parser.parse_args()
    return args


def get_parsers():
    return [ByflyParser, MTS_Parser, UNETParser]


def get_parser_by_name(parsers, name):
    parser = None
    for parser_cls in parsers:
        if parser_cls.PARSER_NAME.lower() == name.lower():
            parser = parser_cls()
            return parser
    else:
        raise NameError("Incorrect parser name")


def main():
    parsers = get_parsers()
    exporter = CSV_Exporter()

    args = parse_args()

    if not args.name:
        print("No parser name specified")
        return

    parser = get_parser_by_name(parsers, args.name)

    points = parser.get_points()
    exporter.export_points(args.path, points)

if __name__ == '__main__':
    main()
