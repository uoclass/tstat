"""
Command-line interface for tstat
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

# program and release information
PROGRAM_NAME = "tstat CLI"
RELEASE_VERSION = """(not a release build)
Run git log to view last commit
Download latest release from https://github.com/uoclass/tstat/releases"""
PROGRAM_AUTHORS = "by Alex JPS, Eric Edwards, Alexa Roskowski"

# constants
COLORS: list[str] = ["white", "black", "gray", "yellow", "red", "blue", "green", "brown", "pink", "orange", "purple"]
DATE_FORMATS: list[str] = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d.%m.%Y", "%d.%m.%y"]
QUERY_TYPES = ["perweek", "perbuilding", "perroom", "perrequestor", "showtickets"]
DEFAULT_TRACEBACK = 0
DEBUG_TRACEBACK = 3

# for args that may be included in a config file
STANDARD_ARGS = ["localreport", "name", "color", "termstart", "termend", "weeks", "building", "remail", "rname",
                 "rphone", "diagnoses", "anddiagnoses", "head", "tail", "querytype", "daliases"]
# args that should not be in a config file
EXCLUDE_ARGS = ["version", "debug", "nographics", "printquery", "saveconfig", "config"]

# default name of diagnoses aliases file
DEFAULT_DIAGNOSES_ALIASES_FILE = "diagnoses.json"


class BadArgError(ValueError):
    """
    Exception class for errors stemming from bad user input.
    Currently extends ValueError.
    """
    pass


def check_file(filename: str, filetype: str) -> bool:
    """
    True if given filename exists and is of desired type, else False.
    This does not check for anything within contents of file itself.
    """
    if not filename:
        # no filename provided
        return False
    filename = filename.strip()
    if not (os.path.exists(filename)):
        # file does not exist
        return False
    if (os.path.splitext(filename)[-1].lower()) != f".{filetype.lower()}":
        # file extension not of desired filetype
        return False
    return True


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
    This expects a fully completed args dict.
    i.e. called after load_config(), if applicable.
    """
    # Debug stipulations
    if not args.get("debug") and args.get("nographics"):
        raise BadArgError("Cannot pass --nographics without --debug flag")
    if not args.get("debug") and args.get("printquery"):
        raise BadArgError("Cannot pass --printquery without --debug flag")

    # Must select a querytype if not loading
    if not args.get("config") and args.get("querytype") not in QUERY_TYPES:
        raise BadArgError("Must select a query type")

    # Query result cropping stipulations
    if args.get("head") is not None and args.get("tail") is not None:
        raise BadArgError("Cannot pass --head and --tail simultaneously")
    if args.get("head") is not None and args.get("head") < 0:
        raise BadArgError(f"Cannot pass --head {args['head']}, pass at least 1")
    if args.get("tail") is not None and args.get("tail") < 0:
        raise BadArgError(f"Cannot pass --tail {args['tail']}, pass at least 1")

    # Stipulations for perbuilding
    if args["querytype"] == "perbuilding" and args.get("building"):
        raise BadArgError("Cannot filter to a single building in a perbuilding query")

    # Stipulations for perweek
    if args["querytype"] != "perweek" and args.get("weeks") is not None:
        raise BadArgError("Cannot pass --weeks without --perweek")
    if args.get("weeks") and args.get("termend"):
        raise BadArgError("Cannot pass --weeks and --termend simultaneously")
    if args.get("weeks") is not None and args.get("weeks") < 0:
        raise BadArgError(f"Cannot pass --weeks {args['weeks']}, use at least 1 week")

    # Stipulations for perrequestor
    if args["querytype"] == "perrequestor" and \
            (args.get("remail") or args.get("rname") or args.get("rphone")):
        raise BadArgError("Cannot pass any requestor filters with perrequestor query")

    # Stipulations for showtickets
    if args["querytype"] == "showtickets" and args.get("prune"):
        raise BadArgError("Cannot pass --prune with showtickets query")

    # Stipulations for localreport
    # must have localreport unless saving config
    if not (args.get("saveconfig") or args.get("localreport")):
        raise BadArgError("Must specify a report file using --localreport flag")


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

    # find actual requestor object
    if args.get("remail") or args.get("rname") or args.get("rphone"):
        requestors_filter: list[User] = org.find_user(args.get("remail"),
                                                      args.get("rname"),
                                                      args.get("rphone"))
        # print message based on number of matches
        if len(requestors_filter) == 1:
            print(f"Filtering to requestor {requestors_filter[0]}")
        elif len(requestors_filter) > 1:
            print("Filtering to multiple matching requestors:")
            for requestor in requestors_filter:
                print(f"    {requestor}")
        else:
            raise BadArgError("No requestors found in report matching given filters")
        # set args dict to list of actual requestor objects
        args["requestors"] = requestors_filter

    # set zeroes and empty strings to None
    # helps user pass empty quotes to override json args to None
    for key in STANDARD_ARGS:
        if args.get(key) == "":
            print(f"Empty value passed for {key}, ignoring")
            args[key] = None
        if args.get(key) == 0:
            print(f"Value 0 passed for {key}, ignoring")
            args[key] = None

    # interpret prune flag as bool
    if args.get("prune"):
        if args.get("prune").lower() in ["t", "true", "y", "yes", "on"]:
            args["prune"] = True
        elif args.get("prune").lower() in ["f", "false", "n", "no", "off"]:
            args["prune"] = False
        else:
            raise BadArgError("Pass either true or false for the prune argument")

    # fix names of user-provided diagnoses
    if args.get("diagnoses") or args.get("anddiagnoses"):
        rename_diagnoses(args)


def rename_diagnoses(args: dict) -> None:
    """
    Turn the user-provided diagnoses filter into a list using
    diagnoses display names defined in diagnoses aliases file (if any).
    The diagnoses aliases file in args["daliases"] is expected valid.
    """
    # check whether using "diagnoses" or "anddiagnoses" filter
    diagnoses_filter_type: str
    diagnoses_filter: str
    if args.get("diagnoses"):
        diagnoses_filter_type = "diagnoses"
        diagnoses_filter = args["diagnoses"]
    elif args.get("anddiagnoses"):
        diagnoses_filter_type = "anddiagnoses"
        diagnoses_filter = args["anddiagnoses"]
    else:
        # no diagnoses filtering at all
        raise ValueError("Neither 'diagnoses' nor 'anddiagnoses' contain values")

    # split string into list and strip diagnoses names
    diagnoses_list: list[str] = diagnoses_filter.split(",")
    for i in range(len(diagnoses_list)):
        diagnoses_list[i] = "".join(
            char.lower() for char in diagnoses_list[i] if char.isalpha()
        )

    # if no diagnoses aliases file, finish here
    if not args.get("daliases"):
        args[diagnoses_filter_type] = diagnoses_list
        return

    # diagnoses aliases file present
    aliases_file: typing.TextIO = open(args["daliases"], mode="r", encoding="utf-8-sig")
    alias_mappings: dict[str, str] = json.load(aliases_file)

    # replace diagnoses with display names from diagnoses aliases file
    # if no alias mapping, just keep original diagnosis name
    for i in range(len(diagnoses_list)):
        # canonize string to use as key to find mapping
        canon_diagnosis: str = "".join(
            char for char in diagnoses_list[i] if char.isalpha()
        )
        if alias_mappings.get(canon_diagnosis):
            # replace with display name if one is given by aliases file
            diagnoses_list[i] = alias_mappings[canon_diagnosis]
    aliases_file.close()

    # give args dict the new diagnoses list
    args[diagnoses_filter_type] = diagnoses_list

def check_report(args: dict, report: Report) -> None:
    """
    For the requested query type,
    Halt program if report does not contain correct info.
    """
    query_type = args["querytype"]
    if query_type == "perweek":
        if "created" not in report.fields_present:
            raise BadArgError("Cannot run tickets-per-week query, no created field in report")
    if query_type == "perbuilding":
        if "building" not in report.fields_present:
            raise BadArgError(
                "Cannot run a tickets-per-building query, no building field in report")
    if query_type == "perroom":
        if ("building" not in report.fields_present) or ("room_identifier" not in report.fields_present):
            raise BadArgError(
                "Cannot run a tickets-per-room query, no building and room identifier fields in report")


def parser_setup():
    """
    Set up argument parser with needed arguments.
    Return the parser.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    # display version
    parser.add_argument("--version", action="store_true", help="Display program version")

    # file io flags
    config_group = parser.add_mutually_exclusive_group(required=False)
    config_group.add_argument("--saveconfig", type=str,
                              help="Save current arguments as a loadable config file with given file name")
    config_group.add_argument("--config", type=str, help="Load configuration file with filename")
    parser.add_argument("--localreport", "-l", type=str, help="Load report csv file")
    parser.add_argument("--daliases", type=str, help="Load JSON mapping aliases to valid diagnoses names")

    # debug mode
    parser.add_argument("--debug", action="store_true", help="Show traceback for all errors")
    parser.add_argument("--nographics", action="store_true", help="Do not show graph")
    parser.add_argument("--printquery", action="store_true", help="Always print query results")

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
    # requestor filters
    parser.add_argument("--remail", type=str, help="Specify requestor email.")
    parser.add_argument("--rname", type=str, help="Specify requestor name.")
    parser.add_argument("--rphone", type=str, help="Specify requestor phone.")

    # two possible diagnoses filters (OR search, AND search)
    diag_group = parser.add_mutually_exclusive_group(required=False)
    diag_group.add_argument("-d", "--diagnoses", type=str, help="Specify diagnoses 'OR' filter, comma-separated.")
    diag_group.add_argument("--anddiagnoses", type=str, help="Specify diagnoses 'AND' filter, comma-separated.")

    # result cropping
    crop_group = parser.add_mutually_exclusive_group(required=False)
    crop_group.add_argument("--head", type=int, help="Show only first X entries from query results")
    crop_group.add_argument("--tail", type=int, help="Show only last X entries from query results")
    crop_group.add_argument("--prune", type=str, help="Set true to always hide graph bars with 0 count")

    # query presets
    parser.add_argument("-q", "--querytype", choices=QUERY_TYPES, help="Specify query type")

    return parser


def run_query(args: dict, org: Organization) -> Union[dict, list[Ticket]]:
    """
    Run query with given args on given org.
    Return results, call appropriate visual.py function.
    """
    query_type: dict = args["querytype"]
    query_result: Union[dict, list[Ticket]] = {}

    # determine query, run, and save results
    if query_type == "perweek":
        tickets_per_week = org.per_week(args)
        if not args.get("nographics"):
            view_per_week(tickets_per_week, args)
        query_result = tickets_per_week
    if query_type == "perbuilding":
        tickets_per_building = org.per_building(args)
        if not args.get("nographics"):
            view_per_building(tickets_per_building, args)
        query_result = tickets_per_building
    if query_type == "perroom":
        tickets_per_room = org.per_room(args)
        if not args.get("nographics"):
            view_per_room(tickets_per_room, args)
        query_result = tickets_per_room
    if query_type == "perrequestor":
        tickets_per_requestor = org.per_requestor(args)
        if not args.get("nographics"):
            view_per_requestor(tickets_per_requestor, args)
        query_result = tickets_per_requestor
    if query_type == "showtickets":
        tickets_matched: list[Ticket] = filter_tickets(org.tickets, args)
        if not args.get("nographics"):
            view_show_tickets(tickets_matched, args)
        query_result = tickets_matched

    # print query results if option enabled
    if args.get("printquery") and args["querytype"] != "showtickets":
        print(query_result)

    return query_result


def save_config(args_dict: dict, config_path: str):
    """
    Save current arguments into loadable JSON configuration file.
    """

    # remove unneeded arguments for config file
    for arg in EXCLUDE_ARGS:
        args_dict.pop(arg)

    # add correct file extension
    if not config_path.endswith(".json"):
        config_path += ".json"

    file = open(config_path, "w+")
    json.dump(args_dict, file, indent=4)

    print(f"Saved current configuration to {config_path}")

    file.close()


def load_config(args: dict):
    """
    Load configuration file.
    Overwrite json args with user args.
    """
    file = open(args.get("config"))
    json_args = json.load(file)
    file.close()
    args.pop("config")

    # loop thru standard args dict keys
    # substitute json values with user-provided values (if any)
    for arg in STANDARD_ARGS:
        if args.get(arg) is None:
            args[arg] = json_args.get(arg)


def main(argv) -> None:
    """
    Parse arguments, call basic input validation.
    Call run_query() to run and display results.
    """
    # set default traceback
    sys.tracebacklimit = DEFAULT_TRACEBACK

    # need arguments
    if len(argv) < 1:
        raise BadArgError("No arguments provided")

    # set up parsers and parse into dict
    parser: argparse.ArgumentParser = parser_setup()

    args: dict = vars(parser.parse_args(argv))

    # display version if requested
    if args.get("version"):
        print(f"{PROGRAM_NAME} {RELEASE_VERSION}\n{PROGRAM_AUTHORS}")
        exit()

    # set debug mode
    sys.tracebacklimit = DEBUG_TRACEBACK if args.get("debug") else DEFAULT_TRACEBACK

    if args.get("config"):
        load_config(args)

    # if no diagnoses aliases file provided, use default if it's valid
    if not args.get("daliases") and check_file(DEFAULT_DIAGNOSES_ALIASES_FILE, "JSON"):
        args["daliases"] = DEFAULT_DIAGNOSES_ALIASES_FILE

    # atp we expect a fully completed args dict

    # check for errors in args
    check_options(args)

    # FIXME refactor the following section into a validity-checking function

    # check for valid ticket report CSV
    if args.get("localreport") and not check_file(args["localreport"], "CSV"):
        raise BadArgError("Invalid local report CSV file provided")

    # check for valid diagnoses JSON, if provided
    if args.get("daliases") and not check_file(args["daliases"], "JSON"):
        raise BadArgError("Invalid diagnoses aliases JSON file provided")

    # FIXME end section to be refactored into validity-checking function

    # save the (now validated) config to a file if requested
    if args.get("saveconfig"):
        save_config(args, args["saveconfig"])
        return

    # check report has enough info for query
    report = Report(args["localreport"], args["daliases"])
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
