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

class Organization:
    buildings: dict[str, Building]
    users: dict[str, User]
    departments: dict[str, Department]
    groups: dict[str, Group]
    tickets: dict[int, Ticket]

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
            ticket = Ticket(self, row)
            self.tickets[ticket.id] = ticket
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
        if not room_identifer:
            room_identifer = "Other"
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
