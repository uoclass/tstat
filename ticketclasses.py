"""
Ticket Classes for tdxplot
by Eric Edwards, Alex JPS
2023-06-23

Class definitions for tickets, users, rooms, etc.
"""

# Packages
from datetime import *
from enum import * 

class Building:
    name: str
    rooms: dict[str, "Room"]

    def __init__(self, name) -> None:
        self.name = name
        self.rooms = {}

    def __str__(self) -> str:
        return f"Building {self.name}"

    def __repr__(self) -> str:
        return f"Building({self.name})"
    
class Room:
    building: Building
    identifier: str
    tickets: list["Ticket"]

    def __init__(self, building: Building, identifier: str) -> None:
        self.building = building
        self.identifier = identifier
        self.tickets = []

    def __str__(self) -> str:
        return f"Room {self.building.name} {self.identifier}"

    def __repr__(self) -> str:
        return f"Room({self.building.name}, {self.identifier})"

class User:
    """
    A TDX user (typically as requestor on a ticket).
    """
    email: str
    name: str
    phone: str

    def __init__(self, email, name, phone) -> None:
       self.email = email
       self.name = name
       self.phone = phone

    def __str__(self) -> str:
        return f"User {self.email} with name {self.name}"

    def __repr__(self) -> str:
        return f"User({self.email}, {self.name})"

class Group:
    """
    A TDX group (typically as Resp Group on a ticket).
    """
    name: str

    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"Group {self.name}"

    def __repr__(self) -> str:
        return f"Group({self.name})"

class Department:
    """
    A TDX department (typically listed under requestor on a ticket).
    """
    name: str

    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"Department {self.name}"

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
    responsible: Group
    requestor: User
    dept: Department
    room: Room
    created: datetime
    modified: datetime
    status: Status

    def __init__(self, org: "Organization", csv_ticket: dict) -> None:
        self.id = int(csv_ticket["ID"]) if csv_ticket.get("ID") else None
        self.title = csv_ticket.get("Title")
        self.responsible = org.find_group(csv_ticket.get("Resp Group"))
        self.requestor = org.find_user(csv_ticket.get("Requestor"),
                                       csv_ticket.get("Requestor Email"),
                                       csv_ticket.get("Requestor Phone"))
        self.department = org.find_department(csv_ticket.get("Acct/Dept"))
        self.room = org.find_room(csv_ticket.get("Class Support Building"),
                                  csv_ticket.get("Room number"))
        print(self)
        
    def __str__(self) -> str:
        return f"""{self.title}
ID: {self.id}
Responsible: {self.responsible.name}
Requestor: {self.requestor.name}
Department: {self.department.name}
Room: {self.room.building.name} {self.room.identifier}"""

    def __repr__(self) -> str:
        return self.__str__()
