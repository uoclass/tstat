"""
Ticket Organization for tdxplot
by Eric Edwards, Alex JPS
2023-06-23

Organization class and methods for analyzing tickets
and managing Organization attributes (departments, users, etc.)
"""

# Packages
from typing import Union

# Files
from ticketclasses import *

# Constants
DEFAULT_WEEKS = 11
DEFAULT_REQUESTORS = 15


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

    def add_new_ticket(self, ticket: Ticket) -> None:
        """
        Add ticket to self.tickets.
        And add to lists of tickets from on-campus entities.
        """
        # check for valid ticket
        try:
            assert type(ticket.id) == int
            assert type(ticket.created) != str
            assert type(ticket.modified) != str
        except AssertionError:
            raise ValueError("Organization.add_new_ticket() received invalid ticket")

        # add ticket to entities' lists and to org's dict
        self.tickets[ticket.id] = ticket
        ticket.room.tickets.append(ticket)
        ticket.requestor.tickets.append(ticket)
        ticket.responsible_group.tickets.append(ticket)
        ticket.department.tickets.append(ticket)

    def find_group(self, name: str = "Undefined", create_mode: bool = False) -> Group:
        """
        Return group with name if already exists.
        Otherwise add new group and return.
        """
        name = name if name else "Undefined"
        if self.groups.get(name):
            return self.groups[name]
        if create_mode:
            self.groups[name] = Group(name)
            return self.groups[name]
        return None

    def find_user(self, email: str = None, name: str = None, phone: str = None, create_mode: bool = False) -> User:
        """
        Return user with all of given properies, if exists.
        Provide email for fast result (hash lookup).
        Giving only name and/or phone is slower (loop).
        Otherwise add new user with given info and return.
        """
        # fast lookup via email
        if email:
            found: User = self.users.get(email)
            if found and \
                (not name or found.name == name) and \
                (not phone or found.phone == phone):
                return self.users[email]
        elif name or phone:
            # no email, try looping
            for key in self.users:
                current: User = self.users[key]
                if email and current.email != email:
                    continue
                if name and current.name != name:
                    continue
                if phone and current.phone != phone:
                    continue
                return current

        # nothing found, so create if allowed
        if create_mode:
            email = email if email else "Undefined"
            name = name if name else "Undefined"
            phone = phone if phone else "Undefined"
            self.users[email] = User(email, name, phone)
            return self.users[email]

        # nothing found and no creating
        return None

    def find_department(self, name: str = "Undefined", create_mode: bool = False) -> Department:
        """
        Return department with name if already exists.
        Otherwise add new department and return.
        """
        name = name if name else "Undefined"
        if self.departments.get(name):
            return self.departments[name]
        if create_mode:
            self.departments[name] = Department(name)
            return self.departments[name]
        return None

    def find_room(self, building_name: str = "Undefined",
                  room_identifier: str = "Undefined",
                  create_mode: bool = False) -> Room:
        """
        Return room with building name and identifier if already exists.
        Otherwise add new room or building as needed and return.
        """
        building_name = building_name if building_name else "Undefined"
        room_identifier = room_identifier if room_identifier else "Undefined"
        building: Building = self.find_building(building_name, create_mode)
        if building:
            if building.rooms.get(room_identifier):
                return building.rooms[room_identifier]
            if create_mode:
                building.rooms[room_identifier] = Room(building, room_identifier)
                return building.rooms[room_identifier]
        return None

    def find_building(self, name: str = "Undefined", create_mode: bool = False) -> Building:
        """
        Return building with name if already exists.
        If create_mode, return a new building if none found.
        """
        name = name if name else "Undefined"
        if self.buildings.get(name):
            return self.buildings[name]
        if create_mode:
            self.buildings[name] = Building(name)
            return self.buildings[name]
        return None

    def per_week(self, args: dict) -> dict[datetime, int]:
        """
        Return a dict counting tickets per week number.
        This dict can be used as input to graph the information.
        """
        # find first week
        first_week = None
        if args.get("termstart"):
            # start date provided
            first_week: datetime = args["termstart"]
        else:
            # find first week by earliest ticket
            for id in self.tickets:
                if not first_week:
                    first_week: datetime = self.tickets[id].created
                if self.tickets[id].created < first_week:
                    first_week: datetime = self.tickets[id].created
        # use the first day of the week
        first_week = get_monday(first_week)
        print(f"Using {first_week} as first week")

        # find last week
        last_week = None
        if args.get("weeks"):
            # number of weeks provided
            last_week: datetime = first_week + (args["weeks"] - 1) * timedelta(days=7)
        elif args.get("termend"):
            # termend input provided
            end_delta: datetime = args["termend"] - first_week
            num_weeks: int = 1 + (end_delta.days // 7)
            last_week: datetime = get_monday(args["termend"])
            print(f"Using {num_weeks}-week term based on given end date")
        else:
            # none given
            print(f"Using default {DEFAULT_WEEKS}-week term")
            last_week: datetime = first_week + (DEFAULT_WEEKS - 1) * timedelta(days=7)

        # dict of the ticket counts per week
        week_counts: dict[datetime, int] = {}
        week_i: datetime = first_week
        while week_i <= last_week:
            week_counts[week_i] = 0
            week_i += timedelta(days=7)

        # apply filtering AFTER term start decided
        filtered_tickets = filter_tickets(self.tickets, args, ["termstart", "termend"])

        # sort tickets into week_counts
        for ticket in filtered_tickets:
            ticket_week = get_monday(ticket.created)
            if ticket_week >= first_week and ticket_week <= last_week:
                # start counting with week 1
                week_counts[ticket_week] += 1

        # return list of ticket counts per week
        return week_counts

    def per_building(self, args: dict) -> dict[str, int]:
        """
        Return a dict counting tickets per building.
        This dict can be used as input to graph the information.
        """
        # dict for buildings
        building_count: dict[Building, int] = {}

        # run filtering and count on each room
        for building_name in self.buildings:
            building = self.buildings[building_name]
            building_count[building] = 0
            for room_identifier in building.rooms:
                room = building.rooms[room_identifier]
                building_count[building] += len(filter_tickets(room.tickets, args))

        # return dict of counts per building
        return building_count

    def per_room(self, args: dict) -> dict[str, int]:
        """
        Return a dict counting tickets per room within a given building.
        This information is meant to be used as input for graphing purposes.
        """
        # dict for room  to room numbers
        room_count: dict[Room, int] = {}

        # ensure we have a building and not empty/None
        building: Building = args.get("building")
        if building:
            for room_identifier in building.rooms:
                room = building.rooms[room_identifier]
                room_count[room] = len(filter_tickets(room.tickets, args, ["building"]))
        else:
            for bldg in self.buildings.values():
                for rm in bldg.rooms.values():
                    room_count[rm] = len(filter_tickets(rm.tickets, args))

        # return dict of counts per room
        return room_count

    def per_requestor(self, args: dict):
        """
        Return a dict counting tickets by requestor within a given building.
        This information is meant to be used as input for graphing purposes.
        """
        requestor_count: dict[User, int] = {}
        for requestor_id in self.users:
            requestor = self.users[requestor_id]
            requestor_count[requestor] = len(filter_tickets(requestor.tickets, args))

        # return dict of counts per requestor
        return requestor_count


# Helper functions

def get_monday(date: datetime):
    """
    Given datetime, return Monday midnight of that week.
    """
    date: datetime = datetime.combine(date, time(0, 0))
    while datetime.weekday(date):
        date -= timedelta(days=1)
    return date


def filter_tickets(tickets: Union[dict[int, Ticket], list[Ticket]],
                   args: dict,
                   exclude: list[str] = []) -> list[Ticket]:
    """
    Given an iterable (list or dict) of Tickets and args with filters,
    And an (optional) list of filters from args to exclude,
    Return a list containing only tickets that pass all filters.
    """
    if type(tickets) == dict:
        tickets = tickets.values()
    term_start: datetime = None if "termstart" in exclude else args.get("termstart")
    term_end: datetime = None if "termend" in exclude else args.get("termend")
    building: Building = None if "building" in exclude else args.get("building")
    requestor: User = None if "requestor" in exclude else args.get("requestor")

    # handle diagnoses
    diagnoses_strings: list[str] = []
    diagnoses: list[Diagnosis] = []
    and_diagnoses: bool
    if args.get("diagnoses"):
        and_diagnoses = False
        diagnoses_strings = args["diagnoses"]
    if args.get("anddiagnoses"):
        and_diagnoses = True
        diagnoses_strings = args["anddiagnoses"]
    for diagnosis in diagnoses_strings:
        diagnoses.append(Diagnosis(diagnosis))

    # make term_end inclusive of last day
    if term_end:
        term_end += timedelta(days=1)

    filtered: list[Ticket] = []
    for ticket in tickets:
        if building and ticket.room.building != building:
            continue
        if requestor and ticket.requestor != requestor:
            continue
        if term_start and ticket.created < term_start:
            continue
        if term_end and ticket.created > term_end:
            continue
        if diagnoses:
            if and_diagnoses and not set(diagnoses).issubset(set(ticket.diagnoses)):
                # all diagnoses must match for AND filter
                continue
            if not and_diagnoses:
                # only one diagnosis must match for OR filter
                match: bool = False
                for diagnosis in diagnoses:
                    if diagnosis in ticket.diagnoses:
                        match = True
                        break
                if not match:
                    continue
        # add ticket if it passes all filters
        filtered.append(ticket)
    return filtered