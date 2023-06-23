from ticketclasses import *

class Organization:
    buildings: list[Building]
    requestors: list[Contact]

    def __init__(self) -> None:
        pass

    def add_building(self, building: Building) -> None:
        self.buildings.append(building)