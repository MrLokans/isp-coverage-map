from by_isp_coverage.parsers.atlant_parser import AtlantParser
from by_isp_coverage.parsers.byfly_parser import ByflyParser
from by_isp_coverage.parsers.mts_parser import MTS_Parser
from by_isp_coverage.parsers.unet_parser import UNETParser
from by_isp_coverage.parsers.flynet_parser import FlynetParser


def get_parsers():
    """Returns all available parser classes"""
    return [AtlantParser, ByflyParser, FlynetParser, MTS_Parser, UNETParser]


def get_parser_class_by_name(name, parsers=None):
    """Returns parser instance with the given name from supplied list of parsers,
    otherwise raise NameError exception. If no parsers supplied it will use
    all present ones"""
    if parsers is None:
        parsers = get_parsers()
    for parser_cls in parsers:
        if parser_cls.PARSER_NAME.lower() == name.lower():
            return parser_cls
    else:
        raise NameError("Incorrect parser name: {}".format(name))


def get_parser_by_name(name, parsers=None,
                       coordinate_obtainer=None,
                       validator=None):
    """Returns parser instance with the given name from supplied list of parsers,
    otherwise raise NameError exception. If no parsers supplied it will use
    all present ones.
    Validator and coordinate obtainer instances may also be supplied"""
    if parsers is None:
        parsers = get_parsers()
    return get_parser_class_by_name(name, parsers)(coordinate_obtainer,
                                                   validator)
