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
import sys
import os
import datetime

# import files
import plot

# constants
COLORS: list[str] = ["white", "black", "gray", "yellow", "red", "blue", "green", "brown", "pink", "orange", "purple"] 
DATE_FORMATS: list[str] = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d.%m.%Y", "%d.%m.%Y"]

def check_file(filename: str):
    """
    Check that the given filename exists and is a CSV file.
    """
    if not filename:
        print("No file input provided", file=sys.stderr)
        exit(1)
    filename.strip()
    if not (os.path.exists(filename)):
        print("Always include filename as the last argument")
        print(f"File {filename} not found", file=sys.stderr)
        exit(1)
    if (os.path.splitext(filename)[-1].lower()) != ".csv":
            print("Always include filename as the last argument")
            print(f"File {filename} is not a CSV file", file=sys.stderr)
            exit(1)

def check_date(date_text: str):
    """
    Checks that given string adheres to one of DATE_FORMATS.
    Returns datetime object.
    """
    date = None
    for date_format in DATE_FORMATS:
        try:
            date: datetime = datetime.strptime(date_text, date_format)
            break
        except:
            continue
    if not date:
        print(f"Date {date_text} not recognized, try yyyy-mm-dd", file=sys.stderr)
        exit(1)
    return date

def parser_setup():
    """
    Set up argument parser with needed arguments.
    Return the parser.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, help="Set the name of the plot.")
    parser.add_argument("-c", "--color", choices=COLORS, help="Set the color of the plot.")
    parser.add_argument("-t", "--termstart", type=str, help="Set week 1 to week of given mm/dd/yyyy (otherwise first ticket date used)")
    parser.add_argument("-w", "--weeks", type=int, help="Set number of weeks in the term")
    return parser

def main():
    """
    Parse arguments, call basic input validation.
    Call plot.py with args.
    """
    # Check last arg is a valid filename
    filename: str = sys.argv.pop()
    filename.strip()
    check_file(filename)
    
    parser: argparse.ArgumentParser = parser_setup()
    args: dict = vars(parser.parse_args())

    args["filename"] = filename

    # ensure valid date format
    if args.get("termstart"):
        args["termstart"] = check_date(args.get("termstart"))

    # call plot tool
    plot.per_week(args)

if __name__ == "__main__":
    main()
