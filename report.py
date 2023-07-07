"""
Ticket Report for tdxplot
by Eric Edwards, Alex JPS
2023-06-30

Report class and methods for parsing and populating tickets
from the information in a given report.
"""

# Packages
from datetime import *
import csv
import os
import sys
import io

# Files
from organization import *

# Constants
STANDARD_FIELDS = ["ID", "Title", "Resp Group", "Requestor", "Requestor Email", "Requestor Phone", "Acct/Dept", "Class Support Building", "Room number", "Created", "Modified", "Status"]
TIME_FORMATS: list[str] = [
    # 12 hour
    "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M", "%m/%d/%y %H:%M", "%d.%m.%Y %H:%M", "%d.%m.%y %H:%M",
    # 24 hour
    "%Y-%m-%d %I:%M %p", "%m/%d/%Y %I:%M %p", "%m/%d/%y %I:%M %p", "%d.%m.%Y %I:%M %p", "%d.%m.%y %I:%M %p"
]

class Report:
    """
    Class for the given report and its propeties.
    Deals with file I/O and reading CSV.
    """
    time_format: str
    fields_present: str
    filename = str

    def __init__(self, filename: str):
        self.filename = filename
        # set fields present and time format
        csv_file: io.TextIOWrapper = open(self.filename, mode="r", encoding="utf-8-sig")
        any_ticket: dict = next(csv.DictReader(csv_file))
        self.set_fields_present(any_ticket)
        self.set_time_format(any_ticket)
        csv_file.close()

    def populate(self, org: Organization) -> None:
        """
        Given filename, read CSV.
        Populate buildings, rooms, tickets, etc. of given Organization.
        """
        csv_file: io.TextIOWrapper = open(self.filename, mode="r", encoding="utf-8-sig")
        csv_tickets: csv.DictReader = csv.DictReader(csv_file)
        count: int = 0
        for row in csv_tickets:
            # fix row to be a valid, clean ticket dict
            self.clean_ticket_dict(row)
            org.add_new_ticket(row)
            count += 1
        csv_file.close()
        if not count:
            print("Ticket report is empty, exiting...", file=sys.stderr)
            exit(1)

    def clean_ticket_dict(self, csv_ticket: dict) -> None:
        """
        Given a dict representing a CSV row, convert to valid ticket dict.
        i.e. ID, Created, and Modified are not strings.
        """
        # ID should be an int
        csv_ticket["ID"] = int(csv_ticket["ID"]) if csv_ticket.get("ID") else 0
        # Created and Modified should be datetime objects
        if csv_ticket.get("Created"):
            csv_ticket["Created"] = datetime.strptime(csv_ticket["Created"], self.time_format)
        if csv_ticket.get("Modified"):
            csv_ticket["Modified"] = datetime.strptime(csv_ticket["Modified"], self.time_format)

    def set_fields_present(self, csv_ticket: dict) -> None:
        """
        Given an arbitrary csv_ticket dict from report,
        Check which of STANDARD_FIELDS are present in report.
        Set self.fields_present accordingly.
        """
        self.fields_present: list[str] = []
        for field in STANDARD_FIELDS:
            try:
                csv_ticket[field]
                self.fields_present.append(field)
            except:
                pass
        if len(STANDARD_FIELDS) != len(self.fields_present):
            print("""Given report does not follow tdxplot Standard Report guidelines
Expect limited functionality due to missing ticket information""", file=sys.stderr)

    
    def set_time_format(self, csv_ticket: dict) -> None:
        """
        Given an arbitrary csv_ticket dict from report,
        Check that time adheres to one of TIME_FORMATS.
        Returns format string or throws error if no match.
        """
        # check whether a time attribute is present
        if csv_ticket.get("Created"):
            time_text: str = csv_ticket["Created"]
        elif csv_ticket.get("Modified"):
            time_text: str = csv_ticket["Modified"]
        else:
            # no date attributes, so no time format to set
            return
        for try_format in TIME_FORMATS:
            try:
                datetime.strptime(time_text, try_format)
                self.time_format = try_format
                return
            except:
                continue
        print(f"Time {time_text} in report is not a valid time format", file=sys.stderr)
        exit(1)

