import argparse

from .parsers.byfly_parser import ByflyParser
from .parsers.mts_parser import MTS_Parser
from .parsers.unet_parser import UNETParser
from .parsers.flynet_parser import FlynetParser

from .csv_exporter import CSV_Exporter


def parse_args():
    desc = "Get geo data about high-speed internet availability in Minsk and Belarus"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--name", "-n",
                        help="Name of parser to use.", required=True)
    parser.add_argument("--path", "-p",
                        help="name of file (csv) to export data to.",
                        default="data.csv")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--connections", action='store_true',
                       help="Should connections data be exported.")
    group.add_argument("--points", action='store_true',
                       help="Should coordinates data be exported.")
    parser.add_argument('--street', '-s',
                        help="Имя улицы, для которой необходимо проверить наличие подключения.",
                        default="")
    parser.add_argument('--region', '-r',
                        help="Имя области для поиска. (all, Бресткая, Витебская и т.д.)",
                        default="Минск")
    parser.add_argument('--house',
                        help="Номер дома, для которого необходимо проверить подключение.",
                        default=""
                        )
    parser.add_argument('--city', '-c',
                        help="Имя города для поиска.",
                        default=""
                        )
    args = parser.parse_args()
    return args


def get_parsers():
    return [ByflyParser, FlynetParser, MTS_Parser, UNETParser]


def get_parser_by_name(parsers, name):
    for parser_cls in parsers:
        if parser_cls.PARSER_NAME.lower() == name.lower():
            parser = parser_cls()
            return parser
    else:
        raise NameError("Incorrect parser name")


def main():
    exporter = CSV_Exporter()

    args = parse_args()
    parser = get_parser_by_name(get_parsers(), args.name)

    if args.connections:
        connections = parser.get_connections(region=args.region.lower(), city=args.city, street=args.street,
                                             house_number=args.house)
        exporter.export_connections(args.path, connections)

    else:
        points = parser.get_points()
        exporter.export_points(args.path, points)

if __name__ == '__main__':
    main()
