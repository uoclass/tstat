"""
Command-line interface for tdxplot
by Eric Edwards, Alex JPS
2023-06-06

The primary .py file form which the program should run.
Parses user input via command-line arguments.
Also performs basic input validation (e.g. formatting, valid files, etc.)
Passes a dictionary with info to appropriate files or functions.
"""

# libraries
import argparse
import sys
import os
from datetime import datetime, date, timedelta

# files
import plot

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
    if (os.path.splitext(filename)[-1].lower()) != '.csv':
            print("Always include filename as the last argument")
            print(f"File {filename} is not a CSV file", file=sys.stderr)
            exit(1)

def check_date(date_text: str):
    """
    Checks that given string is in mm/dd/yyyy format.
    Returns datetime object.
    """
    try:
        date = datetime.strptime(date_text, "%m/%d/%Y")
    except:
        print(f"Date {date_text} does not follow mm/dd/yyyy format", file=sys.stderr)
        exit(1)
    return date


def main():
    """
    Parse arguments, call basic input validation.
    Call plot.py with args_dict.
    """
    input_filename = sys.argv.pop()
    check_file(input_filename)
    input_filename.strip()

    colors = ['white', 'black', 'gray', 'yellow', 'red', 'blue', 'green', 'brown', 'pink', 'orange', 'purple'] 
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub_command help')
    parser.add_argument('-n', '--name', type=str, help='Set the name of the plot.')
    parser.add_argument('-c', '--color', choices=colors, help='Set the color of the plot.')
    parser.add_argument('-w', '--week', type=str, help='Set week 1 to week of given mm/dd/yyyy (otherwise first ticket date used)')
    args = parser.parse_args()
    args_dict = vars(args)

    # custom values
    args_dict['input'] = input_filename
    if args_dict.get('week'):
        args_dict['week'] = check_date(args_dict.get('week'))

    # call plot tool
    plot.ticketCountPerTerm(args_dict)

if __name__ == "__main__":
    main()
