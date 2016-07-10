from .parsers.byfly_parser import ByflyParser
from .parsers.mts_parser import MTS_Parser
from .parsers.unet_parser import UNETParser
from .parsers.flynet_parser import FlynetParser


def get_parsers():
    return [ByflyParser, FlynetParser, MTS_Parser, UNETParser]


def get_parser_by_name(parsers, name):
    for parser_cls in parsers:
        if parser_cls.PARSER_NAME.lower() == name.lower():
            parser = parser_cls()
            return parser
    else:
        raise NameError("Incorrect parser name")
