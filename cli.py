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
import os
import sys
import argparse
import datetime
import json

# import files
from report import *
from organization import *
from visual import *

# constants
COLORS: list[str] = ["white", "black", "gray", "yellow", "red", "blue", "green", "brown", "pink", "orange", "purple"]
DATE_FORMATS: list[str] = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d.%m.%Y", "%d.%m.%y"]
QUERY_TYPES = ["perweek", "perbuilding", "perroom", "perrequestor", "showtickets"]
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


def get_datetime(date_text: str):
    """
    Checks that given string adheres to one of DATE_FORMATS.
    Returns datetime object. Error if not recognized.
    """
    for date_format in DATE_FORMATS:
        try:
            result_date: datetime = datetime.strptime(date_text, date_format)
            return result_date
        except ValueError:
            continue
    raise BadArgError(f"Date {date_text} not recognized, try yyyy-mm-dd")

def check_options(args: dict) -> None:
    """
    Halt program if conflicting or missing flags given.
    """
    # Debug stipulations
    if not args.get("debug") and args.get("nographics"):
        raise BadArgError("Cannot pass --nographics without --debug flag")

    # Query result cropping stipulations
    if args.get("head") is not None and args.get("tail") is not None:
        raise BadArgError("Cannot pass --head and --tail simultaneously")
    if args.get("head") is not None and args.get("head") < 1:
        raise BadArgError(f"Cannot pass --head {args['head']}, pass at least 1")
    if args.get("tail") is not None and args.get("tail") < 1:
        raise BadArgError(f"Cannot pass --tail {args['tail']}, pass at least 1")

    # Stipulations for --perbuilding
    if args["querytype"] == "perbuilding" and args.get("building"):
        raise BadArgError("Cannot filter to a single building in in a --perbuilding query")

    # Stipulations for --perweek
    if args["querytype"] != "perweek" and args.get("weeks") is not None:
        raise BadArgError("Cannot pass --weeks without --perweek")
    if args.get("weeks") and args.get("termend"):
        raise BadArgError("Cannot pass --weeks and --termend simultaneously")
    if args.get("weeks") is not None and args.get("weeks") < 1:
        raise BadArgError(f"Cannot pass --weeks {args['weeks']}, use at least 1 week")

    # Stipulations for --perrequestor
    if args["querytype"] == "perrequestor" and args.get("requestor"):
        raise BadArgError("Cannot pass --requestor filter with --perrequestor query")

    # Stipulations for --saveconfig
    if not args.get("saveconfig") and not args.get("localreport"):
        raise BadArgError("Must specify a report file")


def clean_args(args: dict, org: Organization) -> None:
    """
    Fix formatting by changing datatypes of some args.
    e.g. Change date-related args to datetime.
    """
    # ensure valid date formats
    if args.get("termstart"):
        args["termstart"] = get_datetime(args["termstart"])
    if args.get("termend"):
        args["termend"] = get_datetime(args["termend"])

    # use building object
    if args.get("building"):
        args["building"] = org.find_building(args["building"])
        if not args["building"]:
            raise BadArgError("No such building found in report")

    # lookup requestor by email, name, or phone
    if args.get("requestor"):
        lookup = args["requestor"]
        requestor: User = org.find_user(email=lookup)
        if not requestor:
            requestor = org.find_user(name=lookup)
        if not requestor:
            requestor = org.find_user(phone=lookup)
        if not requestor:
            raise BadArgError("No such requestor found in report")
        args["requestor"] = requestor

    # split up diagnoses list
    if args.get("diagnoses"):
        args["diagnoses"] = args["diagnoses"].split(", ")
    if args.get("anddiagnoses"):
        args["anddiagnoses"] = args["anddiagnoses"].split(", ")


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
            raise BadArgError(
                "Cannot run a tickets-per-building query without Class Support Building field present in report")
    if query_type == "perroom":
        if ("Class Support Building" not in report.fields_present) or ("Room number" not in report.fields_present):
            raise BadArgError(
                "Cannot run a tickets-per-room query without Class Support Building and Room number field present in report")


def parser_setup():
    """
    Set up argument parser with needed arguments.
    Return the parser.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    # file io flags
    config_group = parser.add_mutually_exclusive_group(required=False)
    config_group.add_argument("--saveconfig", type=str, help="Save current arguments as a loadable config file with given file name")
    config_group.add_argument("--config", type=str, help="Load configuration file with filename")
    parser.add_argument("--localreport", "-l", type=str, help = "Load report csv file")
    # debug mode
    parser.add_argument("--debug", action="store_true", help="Show traceback for all errors")
    parser.add_argument("--nographics", action="store_true", help="Print query results but do not show graph")
    # display customization
    parser.add_argument("-n", "--name", type=str, help="Set the name of the plot.")
    parser.add_argument("-c", "--color", choices=COLORS, help="Set the color of the plot.")
    # filters
    parser.add_argument("-t", "--termstart", type=str,
                        help="Exclude tickets before this date (calendar week for --perweek)")
    parser.add_argument("-e", "--termend", type=str,
                        help="Exclude tickets after this date (calendar week for --perweek)")
    parser.add_argument("-w", "--weeks", type=int, help="Set number of weeks in the term for --perweek")
    parser.add_argument("-b", "--building", type=str, help="Specify building filter.")
    parser.add_argument("-u", "--requestor", type=str, help="Specify requestor filter.")
    # two possible diagnoses filters (OR search, AND search)
    diag_group = parser.add_mutually_exclusive_group(required=False)
    diag_group.add_argument("-d", "--diagnoses", type=str, help="Specify diagnoses 'OR' filter, comma-separated.")
    diag_group.add_argument("--anddiagnoses", type=str, help="Specify diagnoses 'AND' filter, comma-separated.")
    # result cropping
    crop_group = parser.add_mutually_exclusive_group(required=False)
    crop_group.add_argument("--head", type=int, help="Show only first X entries from query results")
    crop_group.add_argument("--tail", type=int, help="Show only last X entries from query results")
    
    # query presets
    parser.add_argument("-q", "--querytype", choices=QUERY_TYPES, help="Specify query type")
    return parser


def run_query(args: dict, org: Organization) -> Union[dict, list[Ticket]]:
    """
    Run query with given args on given org.
    Return results, call appropriate visual.py function.
    """
    query_type = args["querytype"]
    if query_type == "perweek":
        tickets_per_week = org.per_week(args)
        if not args.get("nographics"):
            view_per_week(tickets_per_week, args)
        return tickets_per_week
    if query_type == "perbuilding":
        tickets_per_building = org.per_building(args)
        if not args.get("nographics"):
            view_per_building(tickets_per_building, args)
        return tickets_per_building
    if query_type == "perroom":
        tickets_per_room = org.per_room(args)
        if not args.get("nographics"):
            view_per_room(tickets_per_room, args)
        return tickets_per_room
    if query_type == "perrequestor":
        tickets_per_requestor = org.per_requestor(args)
        if not args.get("nographics"):
            view_per_requestor(tickets_per_requestor, args)
        return tickets_per_requestor
    if query_type == "showtickets":
        tickets_matched: list[Ticket] = filter_tickets(org.tickets, args)
        if not args.get("nographics"):
            view_show_tickets(tickets_matched, args)
        return tickets_matched

def save_config(args_dict: dict, config_path: str):
    # remove 'save' argument for config file
    args_dict.pop("saveconfig")

    # add correct file extension
    if not config_path.endswith(".json"):
        config_path += ".json"
    
    file = open(config_path, "w+")
    json.dump(args_dict, file, indent=4)

    print(f"Saved current configuration to {config_path}")

    file.close()

def main(argv):
    """
    Parse arguments, call basic input validation.
    Call run_query() to run and display results.
    """
    # set default traceback
    sys.tracebacklimit = DEFAULT_TRACEBACK

    # need arguments
    if len(argv) < 2:
        raise BadArgError("No arguments provided")

    # set up parsers and parse into dict
    parser: argparse.ArgumentParser = parser_setup()
    args: dict = vars(parser.parse_args(argv))

    # set debug mode
    sys.tracebacklimit = DEBUG_TRACEBACK if args.get("debug") else DEFAULT_TRACEBACK

    # check for errors in args
    if args.get("localreport"):
        check_file(args["localreport"])
    check_options(args)

    # save config file if requested
    if args.get("saveconfig"):
        save_config(args, args["saveconfig"])
        exit(0)

    # check report has enough info for query
    report = Report(args["localreport"])
    check_report(args, report)

    # populate organization
    org = Organization()
    report.populate(org)

    # clean up args dict with correct object types
    clean_args(args, org)

    # run query and display
    run_query(args, org)


if __name__ == "__main__":
    main(sys.argv[1:])