"""
Ticket Classes for tstat
by Eric Edwards, Alex JPS
2023-06-23

Class definitions for tickets, users, rooms, etc.
"""

# Constants
TICKET_URL = "https://service.uoregon.edu/TDNext/Apps/430/Tickets/TicketDet.aspx?TicketID="

# Packages
from datetime import *
from enum import *

class OrganizationEntity:
    """
    Abstract class for an entity within the organization.
    e.g. buildings, users, groups, departments, etc.
    """

class Building(OrganizationEntity):
    name: str
    rooms: dict[str, "Room"]

    def __init__(self, name) -> None:
        self.name = name
        self.rooms = {}

    def __str__(self) -> str:
        return f"Building {self.name}"

    def __repr__(self) -> str:
        return f"Building({self.name})"


class Room(OrganizationEntity):
    building: Building
    identifier: str
    tickets: list["Ticket"]

    def __init__(self, building: Building, identifier: str) -> None:
        self.building = building
        self.identifier = identifier
        self.tickets = []

    def __str__(self) -> str:
        return f"{self.building.name} {self.identifier}"

    def __repr__(self) -> str:
        return f"Room({self.building.name}, {self.identifier})"


class User(OrganizationEntity):
    """
    A TDX user (typically as requestor on a ticket).
    """
    email: str
    name: str
    phone: str
    tickets: list["Ticket"]

    def __init__(self, email, name, phone) -> None:
        self.email = email
        self.name = name
        self.phone = phone
        self.tickets = []

    def __str__(self) -> str:
        return f"{self.name} ({self.email}, {self.phone})"

    def __repr__(self) -> str:
        return f"User({self.email}, {self.name}, {self.phone})"


class Group(OrganizationEntity):
    """
    A TDX group (typically as Resp Group on a ticket).
    """
    name: str
    tickets: list["Ticket"]

    def __init__(self, name) -> None:
        self.name = name
        self.tickets = []

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"Group({self.name})"


class Department(OrganizationEntity):
    """
    A TDX department (typically listed under requestor on a ticket).
    """
    name: str
    tickets: list["Ticket"]

    def __init__(self, name) -> None:
        self.name = name
        self.tickets = []

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"Department({self.name})"


class Status(Enum):
    CLOSED = 0
    NEW = 1
    IN_PROCESS = 2
    WAITING = 3
    ON_HOLD = 4
    SCHEDULED = 5
    OTHER = 6

class Ticket:
    id: int
    title: str
    responsible_group: Group
    requestor: User
    department: Department
    room: Room
    created: datetime
    modified: datetime
    diagnoses: set[str]
    status: Status

    def __init__(self) -> None:
        """
        A ticket does not do anything on initialization.
        It is expected that Report.dict_to_ticket populates
        the ticket attributes based on a CSV ticket.
        """
        pass

    def __str__(self) -> str:
        # diagnoses
        diagnoses_string: str
        if not self.diagnoses:
            diagnoses_string = "None given"
        else:
            diagnoses_string = ", ".join(diagnosis for diagnosis in self.diagnoses)
        return f"""{self.title}
{TICKET_URL}{self.id}
ID: {self.id}
Responsible: {self.responsible_group}
Requestor: {self.requestor}
Department: {self.department}
Room: {self.room}
Created: {self.created}
Modified: {self.modified}
Diagnoses: {diagnoses_string}
Status: {self.status}"""

    def __repr__(self) -> str:
        return self.__str__()