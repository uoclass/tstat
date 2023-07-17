"""
Command-line interface for tdxplot
by Eric Edwards, Alex JPS
2023-06-06

The primary .py file form which the program should run.
Parses user input via command-line arguments.
Also performs basic input validation (e.g. formatting, valid files, etc.)
Passes a dictionary with info to appropriate files or functions.
"""

# import libraries
import argparse
import datetime

# import files
from report import *
from organization import *
from visual import *

# constants
COLORS: list[str] = ["white", "black", "gray", "yellow", "red", "blue", "green", "brown", "pink", "orange", "purple"]
DATE_FORMATS: list[str] = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d.%m.%Y", "%d.%m.%Y"]
QUERY_TYPES = ["perweek", "perbuilding", "perroom", "perrequestor"]
DEFAULT_TRACEBACK = 0
DEBUG_TRACEBACK = 3


class BadArgError(ValueError):
    """
    Exception class for errors stemming from bad user input.
    Currently extends ValueError.
    """
    pass


def check_file(filename: str):
    """
    Check that the given filename exists and is a CSV file.
    """
    if not filename:
        raise BadArgError("No file input provided")
    filename.strip()
    if not (os.path.exists(filename)):
        raise BadArgError(f"File {filename} not found. Include a valid filename as last argument")
    if (os.path.splitext(filename)[-1].lower()) != ".csv":
        raise BadArgError(f"File {filename} is not a CSV. Include a valid filename as last argument")


def check_date(date_text: str):
    """
    Checks that given string adheres to one of DATE_FORMATS.
    Returns datetime object.
    """
    for date_format in DATE_FORMATS:
        try:
            result_date: datetime = datetime.strptime(date_text, date_format)
            return result_date
        except ValueError:
            continue
    raise ValueError(f"Date {date_text} not recognized, try yyyy-mm-dd")


def set_query_type(args: dict) -> None:
    """
    Look at the mutually-exclusive args for query types.
    Set "querytype" value to the correct one.
    """
    for try_type in QUERY_TYPES:
        if args.get(try_type):
            if args.get("querytype"):
                raise ValueError("Pass exactly one query type argument (e.g. --perweek)")
            args["querytype"] = try_type


def check_options(args: dict) -> None:
    """
    Halt program if conflicting or missing flags given.
    """
    # Debug stipulations
    if not args.get("debug") and args.get("nographics"):
        raise BadArgError("Cannot pass --nographics without --debug flag")
    # Stipulations for --perroom
    if args.get("perroom") and not args.get("building"):
        raise BadArgError("No building specified, please specify a building for --perroom using --building [BUILDING_NAME].")

    # Stipulations for --perbuilding
    if args.get("perbuilding") and args.get("building"):
        raise BadArgError("Cannot filter to a single building in in a --perbuilding query")

    # Stipulations for --perweek
    if not args.get("perweek") and args.get("weeks") != None:
        raise BadArgError("Cannot pass --weeks without --perweek")
    if args.get("weeks") and args.get("termend"):
        raise BadArgError("Cannot pass --weeks and --termend simultaneously")
    if args.get("weeks") == 0:
        raise BadArgError("Cannot pass --weeks 0, use at least 1 week")



def clean_args(args: dict, org: Organization) -> None:
    """
    Fix formatting by changing datatypes of some args.
    e.g. Change date-related args to datetime.
    """
    # ensure valid date formats
    if args.get("termstart"):
        args["termstart"] = check_date(args["termstart"])
    if args.get("termend"):
        args["termend"] = check_date(args["termend"])

    # use building object
    if args.get("building"):
        args["building"] = org.find_building(args["building"])
        if not args["building"]:
            raise BadArgError("No such building found in report")


def check_report(args: dict, report: Report) -> None:
    """
    For the requested query type,
    Halt program if report does not contain correct info.
    """
    query_type = args["querytype"]
    if query_type == "perweek":
        if "Created" not in report.fields_present:
            raise BadArgError("Cannot run a tickets-per-week query without Created field present in report")
    if query_type == "perbuilding":
        if "Class Support Building" not in report.fields_present:
            raise BadArgError("Cannot run a tickets-per-building query without Class Support Building field present in report")
    if query_type == "perroom":
        if ("Class Support Building" not in report.fields_present) or ("Room number" not in report.fields_present):
            raise BadArgError("Cannot run a tickets-per-room query without Class Support Building and Room number field present in report")


def parser_setup():
    """
    Set up argument parser with needed arguments.
    Return the parser.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    # debug mode
    parser.add_argument("-d", "--debug", action="store_true", help="Show traceback for all errors")
    # display customization
    parser.add_argument("-n", "--name", type=str, help="Set the name of the plot.")
    parser.add_argument("-c", "--color", choices=COLORS, help="Set the color of the plot.")
    parser.add_argument("--nographics", action="store_true", help="Print query results but do not show graph")
    # filters
    parser.add_argument("-t", "--termstart", type=str,
                        help="Exclude tickets before this date (calendar week for --perweek)")
    parser.add_argument("-e", "--termend", type=str,
                        help="Exclude tickets after this date (calendar week for --perweek)")
    parser.add_argument("-w", "--weeks", type=int, help="Set number of weeks in the term for --perweek")
    parser.add_argument("-b", "--building", type=str, help="Specify building filter.")
    # parser.add_argument("-x", "--topx", type=int, help="Specify the top 'x' filter.")
    # query presets
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--perweek", action="store_true", help="Show tickets per week")
    query_group.add_argument("--perbuilding", action="store_true", help="Show tickets per building")
    query_group.add_argument("--perroom", action="store_true", help="Show tickets per room in a specified building.")
    query_group.add_argument("--perrequestor", action="store_true", help="Show ticket counts by requestor.")
    return parser


def main(argv):
    """
    Parse arguments, call basic input validation.
    Call plot.py with args.
    """
    # set default traceback
    sys.tracebacklimit = DEFAULT_TRACEBACK

    # need arguments
    if len(argv) < 2:
        raise BadArgError("No arguments provided")

    # Check last arg is a valid filename
    filename: str = argv.pop()
    filename.strip()
    check_file(filename)

    # set up parsers and parse into dict
    parser: argparse.ArgumentParser = parser_setup()
    args: dict = vars(parser.parse_args(argv))

    # add missing info to args
    args["filename"] = filename

    # set debug mode
    sys.tracebacklimit = DEBUG_TRACEBACK if args.get("debug") else DEFAULT_TRACEBACK

    # check for errors in args
    set_query_type(args)
    check_options(args)

    # check report has enough info for query
    report = Report(args["filename"])
    check_report(args, report)

    # populate organization
    org = Organization()
    report.populate(org)

    # clean up args dict with correct object types
    clean_args(args, org)

    # run query and display
    query_type = args["querytype"]
    if query_type == "perweek":
        tickets_per_week = org.per_week(args)
        if not args.get("nographics"):
            view_per_week(tickets_per_week, args)
    if query_type == "perbuilding":
        tickets_per_building = org.per_building(args)
        if not args.get("nographics"):
            view_per_building(tickets_per_building, args)
    if query_type == "perroom":
        tickets_per_room = org.per_room(args)
        if not args.get("nographics"):
            view_per_room(tickets_per_room, args)
    if query_type == "perrequestor":
        tickets_per_requestor = org.per_requestor(args)
        if not args.get("nographics"):
            view_per_requestor(tickets_per_requestor, args)
    


if __name__ == "__main__":
    main(sys.argv[1:])
