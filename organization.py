"""
Ticket Organization for tdxplot
by Eric Edwards, Alex JPS
2023-06-23

Organization class and methods for analyzing tickets
and managing Organization attributes (departments, users, etc.)
"""

# Packages
import os
import sys
from datetime import *
import io

# Files
from ticketclasses import *

# Constants
DEFAULT_WEEKS = 11

class Organization:
    """
    Class representing the internal workings of an organization.
    In this case, the organization is the University of Oregon.
    """
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

    def add_new_ticket(self, ticket_dict: dict) -> None:
        """
        Given a valid, clean ticket dict, create a new Ticket object.
        Add that ticket to self.tickets.
        """
        # check for valid ticket dict
        try:
            assert type(ticket_dict["ID"]) == int
            assert type(ticket_dict.get("Created")) != str
            assert type(ticket_dict.get("Modified")) != str
        except:
            print("Organization.add_new_ticket() received invalid ticket dict", file=sys.stderr)
            exit(1)

        # create new ticket
        new_ticket: Ticket = Ticket()

        # populate simple attributes
        new_ticket.id = ticket_dict.get("ID")
        new_ticket.title = ticket_dict.get("Title")
        new_ticket.created = ticket_dict.get("Created")
        new_ticket.modified = ticket_dict.get("Modified")

        # use find methods set these attributes
        new_ticket.responsible = self.find_group(ticket_dict.get("Resp Group"))
        new_ticket.requestor = self.find_user(ticket_dict.get("Requestor"),
                                       ticket_dict.get("Requestor Email"),
                                       ticket_dict.get("Requestor Phone"))
        new_ticket.department = self.find_department(ticket_dict.get("Acct/Dept"))
        new_ticket.room = self.find_room(ticket_dict.get("Class Support Building"),
                                  ticket_dict.get("Room number"))
        
        # Add new ticket to organization's ticket dict
        self.tickets[new_ticket.id] = new_ticket
 
    def find_group(self, name: str) -> Group:
        """
        Return group with name if already exists.
        Otherwise add new group and return.
        """
        if not name:
            name = "Undefined"
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
            email = "Undefined"
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
            name = "Undefined"
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
            building_name = "Undefined"
        if not room_identifier:
            room_identifier = "Undefined"
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
            name = "Undefined"
        if self.buildings.get(name):
            return self.buildings[name]
        self.buildings[name] = Building(name)
        return self.buildings[name]
    
    def per_week(self, args) -> list[int]:
        """
        Return a list counting tickets per week.
        This list can be used as input to graph the information.
        """
        # number of weeks
        num_weeks = args.get("weeks") if args.get("weeks") else DEFAULT_WEEKS

        # list of the ticket counts per week
        week_counts = [0] * num_weeks

        # find start date
        first_day = None
        if args.get("termstart"):
            # start date provided
            first_day: datetime = args["termstart"]
        else:
            # find start date by earliest ticket
            for id in self.tickets:
                if not first_day:
                    first_day: datetime = self.tickets[id].created
                if self.tickets[id].created < first_day:
                    first_day: datetime = self.tickets[id].created

        # use the first day of the week
        first_day = get_monday(first_day)
        print(f"Using {first_day} as term start")

        # sort tickets into week_counts
        for id in self.tickets:
            delta: datetime = self.tickets[id].created - first_day
            week: int = delta.days // 7
            if week < 0 or week >= num_weeks:
                continue
            week_counts[week] += 1

        # return list of ticket counts per week
        return week_counts

    def per_building(self, args) -> dict[str, int]:
        """
        Return a dict counting tickets per building.
        This dict can be used as input to graph the information.
        """
        # dict for buildings
        building_count: dict = {}

        term_start: datetime = args.get("termstart")

        for id in self.tickets:
            # discard tickets before termstart
            if term_start and self.tickets[id].created < term_start:
                continue

            # update building counts
            current_building = self.tickets[id].room.building
            if building_count.get(current_building) != None:
               building_count[current_building] += 1
            else:
                building_count[current_building] = 1

        # return dict of ticket counts per building
        return building_count
        
# Helper functions

def get_monday(date: datetime):
    """
    Given datetime, return Monday midnight of that week.
    """
    date: datetime = datetime.combine(date, time(0, 0))
    while datetime.weekday(date):
        date -= timedelta(days=1)
    return date
