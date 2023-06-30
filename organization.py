"""
Ticket Organization for tdxplot
by Eric Edwards, Alex JPS
2023-06-23

Organization class and methods for parsing and populating tickets
in the classes defined in ticketclasses.py.
"""

# Packages
import csv
import os
import sys
from datetime import *
import io

# Files
from ticketclasses import *

# Constants
STANDARD_FIELDS = ["ID", "Title", "Resp Group", "Requestor", "Requestor Email", "Requestor Phone", "Acct/Dept", "Class Support Building", "Room number", "Created", "Modified", "Status"]
TIME_FORMATS: list[str] = [
    # 12 hour
    "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M", "%m/%d/%y %H:%M", "%d.%m.%Y %H:%M", "%d.%m.%y %H:%M",
    # 24 hour
    "%Y-%m-%d %I:%M %p", "%m/%d/%Y %I:%M %p", "%m/%d/%y %I:%M %p", "%d.%m.%Y %I:%M %p", "%d.%m.%y %I:%M %p"
]
DEFAULT_WEEKS = 11

class Organization:
    buildings: dict[str, Building]
    users: dict[str, User]
    departments: dict[str, Department]
    groups: dict[str, Group]
    tickets: dict[int, Ticket]
    time_format: str

    def __init__(self) -> None:
        self.buildings = {}
        self.users = {}
        self.departments = {}
        self.groups = {}
        self.tickets = {}
    
    def __str__(self) -> str:
        return f"""buildings: {len(self.buildings)} 
users: {len(self.users)}
departments: {len(self.departments)}
groups: {len(self.groups)}
tickets: {len(self.tickets)}"""

    def __repr__(self) -> str:
        return self.__str__()

    def add_new_ticket(self, csv_ticket: dict) -> None:
        new_ticket: Ticket = Ticket()
        new_ticket.id = int(csv_ticket["ID"]) if csv_ticket.get("ID") else 0
        new_ticket.title = csv_ticket.get("Title")
        new_ticket.responsible = self.find_group(csv_ticket.get("Resp Group"))
        new_ticket.requestor = self.find_user(csv_ticket.get("Requestor"),
                                       csv_ticket.get("Requestor Email"),
                                       csv_ticket.get("Requestor Phone"))
        new_ticket.department = self.find_department(csv_ticket.get("Acct/Dept"))
        new_ticket.room = self.find_room(csv_ticket.get("Class Support Building"),
                                  csv_ticket.get("Room number"))
        
        created: str = csv_ticket.get("Created")
        modified: str = csv_ticket.get("Modified")
        self.time_format = get_time_format(created)
    
        new_ticket.created: datetime = datetime.strptime(created, self.time_format) if created else None
        new_ticket.modified: datetime = datetime.strptime(modified, self.time_format) if modified else None
        
        self.tickets[new_ticket.id] = new_ticket

    def populate(self, args: dict) -> None:
        """
        Given filename, read CSV.
        Populate buildings, rooms, tickets, etc.
        """
        csv_file: io.TextIOWrapper = open(args["filename"], mode="r", encoding="utf-8-sig")
        csv_tickets: csv.DictReader = csv.DictReader(csv_file)
        count = 0
        for row in csv_tickets:
            count += 1
            self.add_new_ticket(row)
            if count == 1:
                check_fields(row)
        csv_file.close()
        if not count:
            print("Ticket report is empty, exiting...", file=sys.stderr)
            exit(1)
        
    def find_group(self, name: str) -> Group:
        """
        Return group with name if already exists.
        Otherwise add new group and return.
        """
        if not name:
            name = "Other"
        if self.groups.get(name):
            return self.groups[name] 
        self.groups[name] = Group(name)
        return self.groups[name]

    def find_user(self, email: str, name: str, phone: str) -> User:
        """
        Return user with given email if already exists.
        Otherwise add new user with given info and return.
        """
        if not email:
            email = "Other"
        if self.users.get(email):
            return self.users[email]
        self.users[email] = User(email, name, phone)
        return self.users[email]

    def find_department(self, name: str) -> Department:
        """
        Return department with name if already exists.
        Otherwise add new department and return.
        """
        if not name:
            name = "Other"
        if self.departments.get(name):
            return self.departments[name] 
        self.departments[name] = Department(name)
        return self.departments[name]

    def find_room(self, building_name: str, room_identifier: str) -> Room:
        """
        Return room with building name and identifier if already exists.
        Otherwise add new room or building as needed and return.
        """
        if not building_name:
            building_name = "Other"
        if not room_identifier:
            room_identifier = "Other"
        building: Building = self.find_building(building_name)
        if building.rooms.get(room_identifier):
            return building.rooms[room_identifier]
        building.rooms[room_identifier] = Room(building, room_identifier)
        return building.rooms[room_identifier]

    def find_building(self, name) -> Building:
        """
        Return building with name if already exists.
        Otherwise add new building and return.
        """
        if not name:
            name = "Other"
        if self.buildings.get(name):
            return self.buildings[name]
        self.buildings[name] = Building(name)
        return self.buildings[name]
    
    def per_week(self, args) -> list[int]:
        first_ticket = self.tickets[list(self.tickets.keys())[0]]
        # number of weeks
        num_weeks = args.get("weeks") if args.get("weeks") else DEFAULT_WEEKS

        # list of the counts of tickets per week
        week_counts = [0] * num_weeks

        if args.get("termstart"):
            first_day = args["termstart"]
        else:
            first_day = first_ticket.created
        first_day = get_monday(first_day)

        for id in self.tickets:
            # figure out which week the ticket is in
            delta: datetime = self.tickets[id].created - first_day
            week: int = delta.days // 7
            if week < 0 or week >= num_weeks:
                continue
            # add to the count of which week it's in
            week_counts[week] += 1
        
        return week_counts

# Helper functions

def check_fields(csv_ticket: dict) -> None:
    """
    Check that the required fields are present in a ticket dict.
    """
    try:
        for field in STANDARD_FIELDS:
            csv_ticket[field]
    except:
        print("Your ticket report does not follow standard tdxplot guidelines")

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

def get_monday(date: datetime):
    """
    Given datetime, return Monday midnight of that week.
    """
    date: datetime = datetime.combine(date, time(0, 0))
    while datetime.weekday(date):
        date -= timedelta(days=1)
    return date