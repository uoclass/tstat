"""
Ticket Sorting for tdxplot
by Alexa Roskowski, Alex JPS
2023-02-16

Takes dictionary of info called by cli.py.
Sorts tickets and displays graph from info in a CSV file from a TDX Report.
Report must at least contain Responsible Group and Modified.
"""

# import libraries
import csv
import os
import sys
from datetime import *
import io
from matplotlib import pyplot

TIME_FORMATS: list[str] = [
    # 12 hour
    "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M", "%m/%d/%y %H:%M", "%d.%m.%Y %H:%M", "%d.%m.%y %H:%M",
    # 24 hour
    "%Y-%m-%d %I:%M %p", "%m/%d/%Y %I:%M %p", "%m/%d/%y %I:%M %p", "%d.%m.%Y %I:%M %p", "%d.%m.%y %I:%M %p"
]

def per_week(args):
    check_fields(args["filename"])
    csv_file: io.TextIOWrapper = open(args["filename"], mode="r")
    csv_tickets: csv.DictReader = csv.DictReader(csv_file)

    # keep tickets for which USS Classrooms is responsible
    tickets: list[csv.DictReader] = []
    for ticket in csv_tickets:
        if ticket["Resp Group"] == "USS-Classrooms":
            # NOTE implement ticket objects to add to list
            tickets.append(ticket)
    csv_file.close()

    # sort the tickets by the modified date
    time_format: str = get_time_format(tickets[0]["Modified"])
    tickets.sort(key=lambda ticket: datetime.strptime(ticket["Modified"], time_format))

    # number of weeks
    weeks = args.get("weeks") if args.get("weeks") else 11

    # list of the counts of tickets per week
    weekly_count = [0] * weeks

    if args.get("termstart"):
        first_day = args["termstart"]
    else:
        first_day = datetime.strptime(tickets[0]["Modified"], "%m/%d/%Y %H:%M")
    first_day = get_monday(first_day)

    for ticket in tickets:
        # figure out which week the ticket is in
        date: datetime = datetime.strptime(ticket["Modified"], time_format)
        delta: datetime = date - first_day
        week: int = delta.days // 7
        if week < 0 or week >= weeks:
            continue
        # add to the count of whcih week its in
        weekly_count[week] += 1

    # FIXME Refactor this to a separate graphing function or file
    week_counts: list[int] = ["Week " + str(i + 1) for i in range(weeks)]

    # initialize the graph
    fig, ax = pyplot.subplots(figsize=(10, 5))
    if args.get("color"):
        ax.bar(week_counts, weekly_count, color=args.get("color"))
    else:
        ax.bar(week_counts, weekly_count, color="green")

    # pyplot.xlabel("Weeks") # removed cause each bar is labeled Week (num)
    ax.set_ylabel("Count")
    if args.get("name"):
        ax.set_title(args.get("name"))
    else:
        ax.set_title("Number of Tickets Per Week")

    rect = ax.patches
    for rect, c in zip(rect, weekly_count):
        # add the count to the graph
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2,
            height + 0.01,
            c,
            horizontalalignment = "center",
            verticalalignment = "bottom",
            color = "Black",
            fontsize = "medium"
        )

    pyplot.show()

def check_fields(filename):
    """
    Check that the required fields are present in file.
    """
    file: io.TextIOWrapper = open(filename, mode="r")
    file_read: str = file.readlines()
    if not "Resp Group" in file_read[0]:
        print("File input does not contain Resp Group", file=sys.stderr)
        exit(1)
    if not "Modified" in file_read[0]:
        print("File input does not contain Modified", file=sys.stderr)
        exit(1)
    file.close()

def get_monday(date: datetime):
    """
    Given datetime, return Monday midnight of that week.
    """
    date: datetime = datetime.combine(date, time(0, 0))
    while datetime.weekday(date):
        date -= timedelta(days=1)
    return date

def get_time_format(time_text: str):
    """
    Checks that time adheres to one of TIME_FORMATS.
    Returns format string or throws error if no match.
    """
    time_text.strip()
    for time_format in TIME_FORMATS:
        try:
            datetime.strptime(time_text, time_format)
            return time_format
        except:
            continue
    print(f"Time {time_text} not recognized, try yyyy-mm-dd hh:mm", file=sys.stderr)
    exit(1)

def run_year_report(args):
    check_fields(args["filename"])
    csv_file: io.TextIOWrapper = open(args["filename"], mode="r")
    csv_tickets: csv.DictReader = csv.DictReader(csv_file)

    # keep tickets in each building
    buildings = {}
    # tickets: list[csv.DictReader] = []
    
    for ticket in csv_tickets:
        building = ticket["Class Support Building"]
        classroom = ticket["Room number"]

        if building not in buildings:
            buildings[building] = {classroom: 0}

        buildings[building].append(ticket)

    res = sorted(buildings, key=lambda key: len(buildings[key]))
    for word in res:
        print(word, "has", len(buildings[word]), "tickets")
        
        # print(building, 'has', len(buildings[building]), 'tickets')

    csv_file.close()