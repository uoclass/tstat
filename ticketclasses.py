from datetime import *


class Building:
    building_id: str
    classrooms: dict
    rooms: list['Room']

    def __init__(self, building_id) -> None:
        self.building_id = building_id
        self.classrooms = {}
    
    def increment_classroom_tickets(self, class_id: str):
        # look for the classroom in the current building, initialize if not found
        if not self.classrooms[class_id]:
            self.classrooms[class_id] = 0
        
        # increment amount of tickets in given classroom
        self.classrooms[class_id] += 1

class Room:
    building: Building
    identifier: str
    tickets: list['Ticket']

class Contact:
    name: str
    email: str

class Account:
    name: str
    id: int

class Ticket:
    id: int
    title: str
    responsible: Contact
    requestor: Contact
    created: datetime
    modified: datetime
    room: Room
    dept: Account

    def __init__(self, building_id: str, classroom: str) -> None:
        pass



