"""
Unit Tests for tdxplot
by Eric Edwards, Alex JPS
2023-07-06

Unit testing for all tdxplot files
"""

import context
import unittest
from report import *
from cli import *


class TestOrganization(unittest.TestCase):
    """
    Test cases for the organization.py,
    The Organization class and helper functions.
    """

    def test_add_new_ticket(self):
        """
        Test Organization.add_new_ticket() method.
        Ensure ticket is added to org.tickets dict
        And to on-campus entities' ticket lists.
        """
        # setup
        org = Organization()
        building1: Building = org.find_building("Building", create_mode=True)
        room1: Room = org.find_room("Building", "1", create_mode=True)
        user1: User = org.find_user("User", create_mode=True)[0]
        group1: Group = org.find_group("Group", create_mode=True)
        dept1: Department = org.find_department("Department", create_mode=True)

        # dummy ticket
        ticket: Ticket = Ticket()
        ticket.id = 1
        ticket.room = room1
        ticket.requestor = user1
        ticket.responsible_group = group1
        ticket.department = dept1

        org.add_new_ticket(ticket)

        # lists updated
        self.assertEqual(room1.tickets, [ticket])
        self.assertEqual(user1.tickets, [ticket])
        self.assertEqual(group1.tickets, [ticket])
        self.assertEqual(dept1.tickets, [ticket])
        self.assertEqual(org.tickets[1], ticket)

    def test_find_group(self):
        """
        Test Organization.find_group() method.
        """
        org = Organization()

        # returns None for nonexistent group
        no_group: Group = org.find_group("The Awesome Group")
        self.assertEqual(no_group, None)

        # returns and adds new group when create_mode
        new_group: Group = org.find_group("The Awesome Group", create_mode=True)
        self.assertTrue(isinstance(new_group, Group))
        self.assertEqual(new_group, org.groups["The Awesome Group"])
        self.assertEqual(new_group.name, "The Awesome Group")

        # name "Undefined" if name skipped
        empty_group: Group = org.find_group(create_mode=True)
        self.assertEqual(empty_group.name, "Undefined")

        # name "Undefined" if empty name
        none_group: Group = org.find_group(None, create_mode=True)
        self.assertEqual(none_group.name, "Undefined")

        # returns existing group now
        my_group: Group = org.find_group("The Awesome Group")
        self.assertEqual(my_group, new_group)

        # still returns existing group when create_mode
        same_group: Group = org.find_group("The Awesome Group", create_mode=True)
        self.assertEqual(same_group, new_group)

    def test_find_user(self):
        """
        Test Organization.find_user() method.
        """
        org = Organization()

        # returns empty list for nonexistent user
        no_user_list: list[User] = org.find_user("realemail@email.net", "AJ", "541541541")
        print(f"no user list is {no_user_list}")
        self.assertEqual(no_user_list, [])

        # returns and adds new user when create_mode
        new_user_list: list[User] = org.find_user("realemail@email.net", "AJ", "541541541", create_mode=True)
        self.assertEqual(len(new_user_list), 1)
        new_user: User = new_user_list[0]
        self.assertTrue(isinstance(new_user, User))
        self.assertEqual([new_user], org.users["realemail@email.net"])
        self.assertEqual(new_user.email, "realemail@email.net")
        self.assertEqual(new_user.name, "AJ")
        self.assertEqual(new_user.phone, "541541541")

        # "Undefined" attributes when omitted
        empty_user_list: list[User] = org.find_user(create_mode=True)
        self.assertEqual(len(empty_user_list), 1)
        empty_user: User = empty_user_list[0]
        self.assertEqual(empty_user.email, "Undefined")
        self.assertEqual(empty_user.name, "Undefined")
        self.assertEqual(empty_user.phone, "Undefined")

        # "Undefined" attributes when None passed
        none_user_list: list[User] = org.find_user(None, None, None, create_mode=True)
        self.assertEqual(len(none_user_list), 1)
        none_user: User = none_user_list[0]
        self.assertEqual(none_user.email, "Undefined")
        self.assertEqual(none_user.name, "Undefined")
        self.assertEqual(none_user.phone, "Undefined")

        # returns existing user now
        my_user_list: list[User] = org.find_user("realemail@email.net")
        self.assertEqual(len(my_user_list), 1)
        my_user: User = my_user_list[0]
        self.assertEqual(my_user, new_user)

        # also works with name or phone or both
        my_user = org.find_user(name="AJ")[0]
        self.assertEqual(my_user, new_user)
        my_user = org.find_user(phone="541541541")[0]
        self.assertEqual(my_user, new_user)
        my_user = org.find_user(None, "AJ", "541541541")[0]
        self.assertEqual(my_user, new_user)

        # still returns existing user when create_mode
        same_user_list: list[User] = org.find_user("realemail@email.net", create_mode=True)
        self.assertEqual(len(same_user_list), 1)
        same_user: User = same_user_list[0]
        self.assertEqual(same_user, new_user)

        # tests involving multiple users with similar information
        org = Organization()

        # correctly creates 4 disparate users
        org.find_user("joe@joe.com", "Joe the Plumber", "0123456789", create_mode=True)
        org.find_user("joe@joe.com", "Joe the Carpenter", "0123456789", create_mode=True)
        org.find_user("joe@joe.com", "Joe the Baker", "0123456789", create_mode=True)
        org.find_user("joe@joe.com", "Undefined", "Undefined", create_mode=True)
        self.assertEqual(len(org.users["joe@joe.com"]), 4)

        # ommitting name and phone matches all users
        all_joes: list[User] = org.find_user(email="joe@joe.com")
        self.assertEqual(all_joes, org.users["joe@joe.com"])

        # ommitting name matches users with same email and phone
        most_joes: list[User] = org.find_user(email="joe@joe.com", phone="0123456789")
        self.assertEqual(most_joes, org.users["joe@joe.com"][:3])

        # including a specific name, email, and phone matches one user
        just_joe: User = org.find_user("joe@joe.com", "Joe the Baker", "0123456789")[0]
        self.assertEqual(just_joe, org.users["joe@joe.com"][2])

    def test_find_department(self):
        """
        Test Organization.find_department() method.
        """
        org = Organization()

        # returns None for nonexistent dept
        no_dept: Department = org.find_department("Department of Redundancy Department")
        self.assertEqual(no_dept, None)

        # returns and adds new dept when create_mode
        new_dept: Department = org.find_department("Department of Redundancy Department", create_mode=True)
        self.assertTrue(isinstance(new_dept, Department))
        self.assertEqual(new_dept, org.departments["Department of Redundancy Department"])
        self.assertEqual(new_dept.name, "Department of Redundancy Department")

        # name "Undefined" if name skipped
        empty_dept: Department = org.find_department(create_mode=True)
        self.assertEqual(empty_dept.name, "Undefined")

        # name "Undefined" if None name
        none_dept: Department = org.find_department(None, create_mode=True)
        self.assertEqual(none_dept.name, "Undefined")

        # returns existing dept now
        my_dept: Department = org.find_department("Department of Redundancy Department")
        self.assertEqual(my_dept, new_dept)

        # still returns existing dept when create_mode
        same_dept: Department = org.find_department("Department of Redundancy Department", create_mode=True)
        self.assertEqual(same_dept, new_dept)

    def test_find_building(self):
        """
        Test Organization.find_building() method.
        """
        org = Organization()

        # returns None for nonexistent bldg
        no_bldg: Building = org.find_building("The Edifice")
        self.assertEqual(no_bldg, None)

        # returns and adds new bldg when create_mode
        new_bldg: Building = org.find_building("The Edifice", create_mode=True)
        self.assertTrue(isinstance(new_bldg, Building))
        self.assertEqual(new_bldg, org.buildings["The Edifice"])
        self.assertEqual(new_bldg.name, "The Edifice")

        # name "Undefined" if name skipped
        empty_bldg: Building = org.find_building(create_mode=True)
        self.assertEqual(empty_bldg.name, "Undefined")

        # name "Undefined" if None name
        none_bldg: Building = org.find_building(None, create_mode=True)
        self.assertEqual(none_bldg.name, "Undefined")

        # returns existing bldg now
        my_bldg: Building = org.find_building("The Edifice")
        self.assertEqual(my_bldg, new_bldg)

        # still returns existing bldg when create_mode
        same_bldg: Building = org.find_building("The Edifice", create_mode=True)
        self.assertEqual(same_bldg, new_bldg)

    def test_find_room(self):
        """
        Test Organization.find_building() method.
        """
        org = Organization()

        # returns None for non-existing room or building combos
        self.assertEqual(None, org.find_room(None, None))
        self.assertEqual(None, org.find_room(None, "False Room"))
        self.assertEqual(None, org.find_room("False Building", None))
        self.assertEqual(None, org.find_room("False Building", "False Room"))
        self.assertEqual([], list(org.buildings.keys()))

        # with create_mode, returns room always
        # adds room to its building and building to org.buildings
        try_room = org.find_room(None, None, create_mode=True)
        self.assertTrue(isinstance(try_room, Room))
        self.assertTrue(isinstance(try_room.building, Building))
        self.assertEqual(try_room.building.name, "Undefined")
        self.assertEqual(try_room.identifier, "Undefined")
        self.assertTrue(isinstance(org.buildings["Undefined"], Building))
        self.assertTrue(isinstance(org.buildings["Undefined"].rooms["Undefined"], Room))

        org = Organization()
        try_room = org.find_room("Some Building", None, create_mode=True)
        self.assertTrue(isinstance(try_room, Room))
        self.assertTrue(isinstance(try_room.building, Building))
        self.assertEqual(try_room.building.name, "Some Building")
        self.assertEqual(try_room.identifier, "Undefined")
        self.assertTrue(isinstance(org.buildings["Some Building"], Building))
        self.assertTrue(isinstance(org.buildings["Some Building"].rooms["Undefined"], Room))

        org = Organization()
        try_room = org.find_room(None, "Some Room", create_mode=True)
        self.assertTrue(isinstance(try_room.building, Building))
        self.assertTrue(isinstance(try_room, Room))
        self.assertEqual(try_room.building.name, "Undefined")
        self.assertEqual(try_room.identifier, "Some Room")
        self.assertTrue(isinstance(org.buildings["Undefined"], Building))
        self.assertTrue(isinstance(org.buildings["Undefined"].rooms["Some Room"], Room))

        org = Organization()
        try_room = org.find_room("Some Building", "Some Room", create_mode=True)
        self.assertTrue(isinstance(try_room, Room))
        self.assertTrue(isinstance(try_room.building, Building))
        self.assertEqual(try_room.building.name, "Some Building")
        self.assertEqual(try_room.identifier, "Some Room")
        self.assertTrue(isinstance(org.buildings["Some Building"], Building))
        self.assertTrue(isinstance(org.buildings["Some Building"].rooms["Some Room"], Room))

        # with no create_mode, existing room returned
        real_room: Room = org.find_room("Some Building", "Some Room")
        self.assertTrue(isinstance(real_room, Room))
        self.assertTrue(isinstance(real_room.building, Building))
        self.assertEqual(real_room.identifier, "Some Room")
        self.assertEqual(real_room.building.name, "Some Building")

    def test_get_monday(self):
        """
        Test cases for get_monday() helper function.
        """
        self.assertEqual(get_monday(datetime(2023, 7, 27), ), datetime(2023, 7, 24))
        self.assertEqual(get_monday(datetime(2023, 6, 26), ), datetime(2023, 6, 26))
        self.assertEqual(get_monday(datetime(2023, 7, 23), ), datetime(2023, 7, 17))

    def test_filter_tickets(self):
        """
        Test cases for filter_tickets() helper function.
        """
        # set up
        report = Report("unit-testing/querytests1.csv")
        org = Organization()
        report.populate(org)
        # using 4 filters here to test "exclude" arg for filter_tickets()
        args: dict = {
            "termstart": datetime(2023, 4, 11),
            "termend": datetime(2023, 5, 29),
            "building": org.find_building("Building3"),
            "requestors": org.find_user(email="requestor1@example.com")
        }
        ticket_dict: dict[int, Ticket] = org.tickets
        ticket_list: list[Ticket] = list(org.tickets.values())

        # termstart and termend filters
        expected: list = [
            org.tickets[2],
            org.tickets[3],
            org.tickets[4],
            org.tickets[5],
            org.tickets[6],
            org.tickets[7],
            org.tickets[8]
        ]
        for type in [ticket_dict, ticket_list]:
            # also test exclude list
            filtered: list[Ticket] = filter_tickets(type, args, ["building", "requestors"])
            self.assertEqual(filtered, expected)

        # building filter
        expected = [
            org.tickets[4],
            org.tickets[5],
            org.tickets[6],
            org.tickets[7],
            org.tickets[8],
            org.tickets[9]
        ]
        for type in [ticket_dict, ticket_list]:
            # also test exclude list
            filtered: list[Ticket] = filter_tickets(type, args, ["termstart", "termend", "requestors"])
            self.assertEqual(filtered, expected)

        # termstart, termend, and building filters
        expected = [
            org.tickets[4],
            org.tickets[5],
            org.tickets[6],
            org.tickets[7],
            org.tickets[8]
        ]
        for type in [ticket_dict, ticket_list]:
            # also test exclude list
            filtered: list[Ticket] = filter_tickets(type, args, ["requestors"])
            self.assertEqual(filtered, expected)

        # requestor filter
        expected = [
            org.tickets[0],
            org.tickets[1],
            org.tickets[2],
            org.tickets[3],
            org.tickets[4],
        ]
        for type in [ticket_dict, ticket_list]:
            # also test exclude list
            filtered: list[Ticket] = filter_tickets(type, args, ["termend", "termstart", "building"])
            self.assertEqual(filtered, expected)

        # diagnoses filter
        # one diagnosis (same for "diagnoses" and "anddiagnoses" filters)
        expected = [
            org.tickets[0],
            org.tickets[1]
        ]
        args = {"diagnoses": [Diagnosis("Touch Panel")]}
        for type in [ticket_dict, ticket_list]:
            filtered: list[Ticket] = filter_tickets(type, args)
            self.assertEqual(filtered, expected)
        args = {"anddiagnoses": [Diagnosis("Touch Panel")]}
        for type in [ticket_dict, ticket_list]:
            filtered: list[Ticket] = filter_tickets(type, args)
            self.assertEqual(filtered, expected)

        # multiple diagnoses ("diagnoses" filter)
        expected = [
            org.tickets[2],
            org.tickets[3],
            org.tickets[4],
            org.tickets[5]
        ]
        args = {"diagnoses": [Diagnosis("Cable--HDMI"), Diagnosis("Cable-Ethernet"), Diagnosis("Projector")]}
        for type in [ticket_dict, ticket_list]:
            filtered: list[Ticket] = filter_tickets(type, args)
            self.assertEqual(filtered, expected)

        # multiple diagnoses ("anddiagnoses" filter)
        expected = [
            org.tickets[2],
        ]
        args = {"anddiagnoses": [Diagnosis("Cable--HDMI"), Diagnosis("Cable-Ethernet"), Diagnosis("Projector")]}
        for type in [ticket_dict, ticket_list]:
            filtered: list[Ticket] = filter_tickets(type, args)
            self.assertEqual(filtered, expected)


class TestQueries(unittest.TestCase):
    """
    Test cases for all queries in the Organization class.
   """

    def test_per_week(self):
        """
        Test cases for per_week() method.
        Also ensures termstart and termend are week-based,
        Unlike normal termstart/end behavior in other queries.
        """
        # setup
        org = Organization()
        report = Report("unit-testing/querytests1.csv")
        report.populate(org)

        # no args
        args: dict = {}
        expected: dict[datetime, int] = {
            datetime(2023, 4, 3): 2,
            datetime(2023, 4, 10): 1,
            datetime(2023, 4, 17): 0,
            datetime(2023, 4, 24): 1,
            datetime(2023, 5, 1): 1,
            datetime(2023, 5, 8): 1,
            datetime(2023, 5, 15): 1,
            datetime(2023, 5, 22): 1,
            datetime(2023, 5, 29): 1,
            datetime(2023, 6, 5): 0,
            datetime(2023, 6, 12): 1,
        }
        self.assertEqual(org.per_week(args), expected)

        # termstart same as first actual ticket date
        args = {"termstart": datetime(2023, 4, 4)}
        self.assertEqual(org.per_week(args), expected)

        # different termstart
        args = {"termstart": datetime(2023, 5, 4)}
        expected = {
            datetime(2023, 5, 1): 1,
            datetime(2023, 5, 8): 1,
            datetime(2023, 5, 15): 1,
            datetime(2023, 5, 22): 1,
            datetime(2023, 5, 29): 1,
            datetime(2023, 6, 5): 0,
            datetime(2023, 6, 12): 1,
            datetime(2023, 6, 19): 0,
            datetime(2023, 6, 26): 0,
            datetime(2023, 7, 3): 0,
            datetime(2023, 7, 10): 0,
        }

        # termstart and weeks specified
        args = {"termstart": datetime(2023, 5, 4), "weeks": 5}
        expected = {
            datetime(2023, 5, 1): 1,
            datetime(2023, 5, 8): 1,
            datetime(2023, 5, 15): 1,
            datetime(2023, 5, 22): 1,
            datetime(2023, 5, 29): 1,
        }
        self.assertEqual(org.per_week(args), expected)

        # termstart and termend specified
        args = {"termstart": datetime(2023, 5, 4), "termend": datetime(2023, 6, 29)}
        expected = {
            datetime(2023, 5, 1): 1,
            datetime(2023, 5, 8): 1,
            datetime(2023, 5, 15): 1,
            datetime(2023, 5, 22): 1,
            datetime(2023, 5, 29): 1,
            datetime(2023, 6, 5): 0,
            datetime(2023, 6, 12): 1,
            datetime(2023, 6, 19): 0,
            datetime(2023, 6, 26): 0,
        }
        self.assertEqual(org.per_week(args), expected)

        # with building filter
        args = {"termend": datetime(2023, 6, 29), "building": org.find_building("Building3")}
        expected = {
            datetime(2023, 4, 3): 0,
            datetime(2023, 4, 10): 0,
            datetime(2023, 4, 17): 0,
            datetime(2023, 4, 24): 0,
            datetime(2023, 5, 1): 1,
            datetime(2023, 5, 8): 1,
            datetime(2023, 5, 15): 1,
            datetime(2023, 5, 22): 1,
            datetime(2023, 5, 29): 1,
            datetime(2023, 6, 5): 0,
            datetime(2023, 6, 12): 1,
            datetime(2023, 6, 19): 0,
            datetime(2023, 6, 26): 0,
        }
        self.assertEqual(org.per_week(args), expected)

        # with requestor filter
        args = {"termend": datetime(2023, 6, 29), "requestors": org.find_user(email="requestor2@example.com")}
        expected = {
            datetime(2023, 4, 3): 0,
            datetime(2023, 4, 10): 0,
            datetime(2023, 4, 17): 0,
            datetime(2023, 4, 24): 0,
            datetime(2023, 5, 1): 0,
            datetime(2023, 5, 8): 1,
            datetime(2023, 5, 15): 1,
            datetime(2023, 5, 22): 1,
            datetime(2023, 5, 29): 0,
            datetime(2023, 6, 5): 0,
            datetime(2023, 6, 12): 0,
            datetime(2023, 6, 19): 0,
            datetime(2023, 6, 26): 0,
        }

        # ensure weeks are given 0 and never omitted
        args = {"termstart": datetime(1970, 1, 1)}
        expected = {
            datetime(1969, 12, 29): 0,
            datetime(1970, 1, 5): 0,
            datetime(1970, 1, 12): 0,
            datetime(1970, 1, 19): 0,
            datetime(1970, 1, 26): 0,
            datetime(1970, 2, 2): 0,
            datetime(1970, 2, 9): 0,
            datetime(1970, 2, 16): 0,
            datetime(1970, 2, 23): 0,
            datetime(1970, 3, 2): 0,
            datetime(1970, 3, 9): 0,
        }
        self.assertEqual(org.per_week(args), expected)

    def test_per_building(self):
        """
        Test cases for per_building() method.
        """
        # setup
        org = Organization()
        report = Report("unit-testing/querytests1.csv")
        report.populate(org)
        building1 = org.find_building("Building1")
        building2 = org.find_building("Building2")
        building3 = org.find_building("Building3")

        # no args
        args: dict = {}
        expected: dict[Building, int] = {
            building1: 1,
            building2: 3,
            building3: 6
        }
        self.assertEqual(org.per_building(args), expected)

        # with termstart
        args = {"termstart": datetime(2023, 4, 23)}
        expected = {
            building1: 0,
            building2: 1,
            building3: 6
        }
        self.assertEqual(org.per_building(args), expected)

        # with termstart and termend
        args = {"termstart": datetime(2023, 4, 10), "termend": datetime(2023, 4, 30)}
        expected = {
            building1: 0,
            building2: 2,
            building3: 0
        }
        self.assertEqual(org.per_building(args), expected)

        # with requestor filter
        args = {"requestors": org.find_user(email="requestor1@example.com")}
        expected = {
            building1: 1,
            building2: 3,
            building3: 1,
        }
        self.assertEqual(org.per_building(args), expected)

    def test_show_tickets(self):
        """
        Test cases for show_tickets() method.
        """
        # setup
        report = Report("unit-testing/querytests1.csv")
        org = Organization()
        report.populate(org)

        # just check that it filters tickets as normal
        args: dict = {"querytype": "showtickets", "debug": True, "nographics": True}
        self.assertEqual(filter_tickets(org.tickets, args), run_query(args, org))

    def test_per_room(self):
        """
        Test cases for per_room() method.
        """
        # setup
        org = Organization()
        report = Report("unit-testing/querytests1.csv")
        report.populate(org)
        building1 = org.find_building("Building1")
        building2 = org.find_building("Building2")
        building3 = org.find_building("Building3")

        # no args
        args: dict = {}
        expected = {
            building1.rooms["1"]: 1,
            building2.rooms["1"]: 1,
            building2.rooms["2"]: 2,
            building3.rooms["1"]: 1,
            building3.rooms["2"]: 1,
            building3.rooms["3"]: 2,
            building3.rooms["4"]: 1,
            building3.rooms["5"]: 1,
        }
        self.assertEqual(org.per_room(args), expected)

        # building filter
        args = {"building": building3}
        expected = {
            building3.rooms["1"]: 1,
            building3.rooms["2"]: 1,
            building3.rooms["3"]: 2,
            building3.rooms["4"]: 1,
            building3.rooms["5"]: 1,
        }
        self.assertEqual(org.per_room(args), expected)

        # requestor filter
        args = {"requestors": org.find_user(email="requestor1@example.com")}
        expected = {
            building1.rooms["1"]: 1,
            building2.rooms["1"]: 1,
            building2.rooms["2"]: 2,
            building3.rooms["1"]: 1,
            building3.rooms["2"]: 0,
            building3.rooms["3"]: 0,
            building3.rooms["4"]: 0,
            building3.rooms["5"]: 0
        }
        self.assertEqual(org.per_room(args), expected)

        # with termstart
        args = {"termstart": datetime(2023, 4, 12)}
        expected = {
            building1.rooms["1"]: 0,
            building2.rooms["1"]: 0,
            building2.rooms["2"]: 1,
            building3.rooms["1"]: 1,
            building3.rooms["2"]: 1,
            building3.rooms["3"]: 2,
            building3.rooms["4"]: 1,
            building3.rooms["5"]: 1,
        }
        self.assertEqual(org.per_room(args), expected)

        # with termstart and termend
        args = {"termstart": datetime(2023, 4, 12), "termend": datetime(2023, 5, 23)}
        expected = {
            building1.rooms["1"]: 0,
            building2.rooms["1"]: 0,
            building2.rooms["2"]: 1,
            building3.rooms["1"]: 1,
            building3.rooms["2"]: 1,
            building3.rooms["3"]: 2,
            building3.rooms["4"]: 0,
            building3.rooms["5"]: 0,
        }
        self.assertEqual(org.per_room(args), expected)

        # with termstart, termend, and building
        args = {
            "termstart": datetime(2023, 5, 8),
            "termend": datetime(2023, 5, 29),
            "building": org.find_building("Building2")
        }
        expected = {
            building3.rooms["1"]: 0,
            building3.rooms["2"]: 1,
            building3.rooms["3"]: 2,
            building3.rooms["4"]: 1,
            building3.rooms["5"]: 0,
        }

    def test_per_requestor(self):
        """
        Test cases for per_requestor() method.
        """
        # setup
        org = Organization()
        report = Report("unit-testing/querytests1.csv")
        report.populate(org)
        requestor1: User = org.find_user("requestor1@example.com")[0]
        requestor2: User = org.find_user("requestor2@example.com")[0]
        requestor3: User = org.find_user("requestor3@example.com")[0]

        # no args
        args: dict = {}
        expected = {
            requestor1: 5,
            requestor2: 3,
            requestor3: 2
        }
        self.assertEqual(org.per_requestor(args), expected)

        # with building filter
        args = {"building": org.find_building("Building3")}
        expected = {
            requestor1: 1,
            requestor2: 3,
            requestor3: 2
        }
        self.assertEqual(org.per_requestor(args), expected)

        # with termstart
        args = {"termstart": datetime(2023, 4, 20)}
        expected = {
            requestor1: 2,
            requestor2: 3,
            requestor3: 2
        }
        self.assertEqual(org.per_requestor(args), expected)

        # with termstart and termend
        args = {"termstart": datetime(2023, 4, 20), "termend": datetime(2023, 5, 27)}
        expected = {
            requestor1: 2,
            requestor2: 3,
            requestor3: 0
        }
        self.assertEqual(org.per_requestor(args), expected)

        # with termstart, termend, and building filter
        args = {"termstart": datetime(2023, 4, 20), "termend": datetime(2023, 5, 27),
                "building": org.find_building("Building2")}
        expected = {
            requestor1: 1,
            requestor2: 0,
            requestor3: 0
        }
        self.assertEqual(org.per_requestor(args), expected)


class TestCli(unittest.TestCase):
    """
    Test cases for command line interface in cli.py.
    """

    def test_no_args(self):
        """
        Ensure BadArgError when no args given.
        """
        argv: list[str] = []
        self.assertRaises(BadArgError, main, argv)

    def test_debug_flag(self):
        """
        Ensure traceback is changed by --debug flag.
        """
        argv: list[str] = ["--debug", "-q", "perweek", "--nographics", "--localreport", "unit-testing/minimal.csv"]
        main(argv)
        self.assertEqual(sys.tracebacklimit, DEBUG_TRACEBACK)

    def test_check_file(self):
        """
        Test cases for check_file() function.
        """
        # bad files
        self.assertRaises(BadArgError, check_file, "unit-testing/no-file.csv")
        self.assertRaises(BadArgError, check_file, "unit-testing/not-a-csv.txt")
        self.assertRaises(BadArgError, check_file, "")

        # expected errors from main()
        argv: list[str] = ["-q", "perweek", "--localreport", "unit-testing/no-file.csv"]
        self.assertRaises(BadArgError, main, argv)
        argv = ["-q", "perweek", "--localreport", "unit-testing/not-a-csv.txt"]
        self.assertRaises(BadArgError, main, argv)
        argv = ["-q", "perweek"]
        self.assertRaises(BadArgError, main, argv)

    def test_get_datetime(self):
        """
        Test cases for get_datetime() function.
        """
        # bad date formats
        self.assertRaises(BadArgError, get_datetime, "19700101")
        self.assertRaises(BadArgError, get_datetime, "January 1, 1970")
        self.assertRaises(BadArgError, get_datetime, "31/12/1970")

        # good date formats
        self.assertEqual(datetime(2020, 12, 31), get_datetime("2020-12-31"))
        self.assertEqual(datetime(2020, 12, 31), get_datetime("12/31/2020"))
        self.assertEqual(datetime(2020, 12, 31), get_datetime("12/31/20"))
        self.assertEqual(datetime(2020, 12, 31), get_datetime("31.12.2020"))
        self.assertEqual(datetime(2020, 12, 31), get_datetime("31.12.20"))

        # expected errors from main()
        argv: list[str] = ["--debug", "--nographics", "--querytype", "perweek", "-t", "19700101", "--localreport",
                           "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

    def test_check_options(self):
        """
        Test cases for check_options() function.
        Tests main(argv) rather than check_options() directly.
        """
        # debug stipulations (pass --nographics without --debug)
        argv: list[str] = ["--nographics", "-q", "perweek", "--localreport", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

        # perbuilding stipulations (pass -b with --perbuilding)
        argv = ["--debug", "--nographics", "-q", "perbuilding", "-b", "Lillis", "--localreport",
                "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

        # perweek stipulations
        # pass -w without --perweek
        argv = ["--debug", "--nographics", "-q", "perbuilding", "-w", "10", "--localreport", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)
        # pass -w and -e at once
        argv = ["--debug", "--nographics", "-q", "perweek", "-w", "10", "-e", "12/31/2023", "--localreport",
                "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

        # perrequestor stipulations
        argv = ["--debug", "--nographics", "-q", "perrequestor", "--remail", "requestor1@example.com",
                "--localreport", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

        # saveconfig stipulations
        # provide none of --localreport, --saveconfig, --config
        argv = ["--debug", "--nographics", "-q", "perweek", "--head", "10"]
        self.assertRaises(BadArgError, main, argv)

    def test_clean_args(self):
        """
        Test cases for clean_args() function.
        """
        org = Organization()
        mybuilding: Building = org.find_building("My Building", create_mode=True)

        # datetimes fixed
        args: dict = {"termstart": "12/31/2020", "termend": "12/31/2020"}
        clean_args(args, org)
        expected: dict = {"termstart": datetime(2020, 12, 31), "termend": datetime(2020, 12, 31)}
        self.assertEqual(args, expected)

        # building object fixed
        args: dict = {"building": "My Building"}
        clean_args(args, org)
        expected: dict = {"building": mybuilding}
        self.assertEqual(args, expected)

    def test_check_report(self):
        """
        Test cases for check_report() function.
        """
        # correct fields present
        org = Organization()
        report = Report("unit-testing/minimal.csv")
        report.populate(org)
        args: dict = {"querytype": "perweek"}
        check_report(args, report)
        args = {"querytype": "perbuilding"}
        check_report(args, report)
        args = {"querytype": "perroom"}
        check_report(args, report)

        # missing fields
        org = Organization()
        report = Report("unit-testing/missing-fields.csv")
        report.populate(org)
        args = {"querytype": "perweek"}
        self.assertRaises(BadArgError, check_report, args, report)
        args = {"querytype": "perbuilding"}
        self.assertRaises(BadArgError, check_report, args, report)
        args = {"querytype": "perroom", "building": "The Building"}
        self.assertRaises(BadArgError, check_report, args, report)

    def test_save_config(self):
        """
        Test cases for save_config() method.
        """
        argv: list[str]

        # sample config 1 (no localreport)
        argv = ["--debug", "--nographics", "--saveconfig", "unit-testing/generated-config1.json", "-q", "perweek",
                "--building", "Building3", "--remail", "requestor2@example.com", "--termstart", "5/15/2023",
                "--weeks", "5"]
        main(argv)
        expected_file: typing.TextIO = open("unit-testing/expected-config1.json", "r")
        generated_file: typing.TextIO = open("unit-testing/generated-config1.json", "r")
        expected: dict = json.load(expected_file)
        generated: dict = json.load(generated_file)
        self.assertEqual(expected, generated)
        expected_file.close()
        generated_file.close()
        os.remove("unit-testing/generated-config1.json")

        # sample config 2 (with localreport)
        argv = ["--debug", "--nographics", "--saveconfig", "unit-testing/generated-config2.json", "-q", "perrequestor",
                "--termstart", "4/4/2023", "--termend", "6/16/2023", "--diagnoses", "Cable--HDMI, Cable-Ethernet",
                "--head", "3", "--name", "Cable Problems by Requestor", "--color", "blue", "--localreport",
                "unit-testing/querytests1.csv"]
        main(argv)
        expected_file: typing.TextIO = open("unit-testing/expected-config2.json", "r")
        generated_file: typing.TextIO = open("unit-testing/generated-config2.json", "r")
        expected: dict = json.load(expected_file)
        generated: dict = json.load(generated_file)
        self.assertEqual(expected, generated)
        expected_file.close()
        generated_file.close()
        os.remove("unit-testing/generated-config2.json")

    def test_load_config(self):
        """
        Test cases for load_config() method.
        """
        # setup
        report: Report = Report("unit-testing/querytests1.csv")
        org: Organization = Organization()
        report.populate(org)

        # load sample config 1
        args: dict = {"config": "unit-testing/expected-config1.json"}
        load_config(args)
        clean_args(args, org)
        # ensure it matches expected args dict
        expected: dict = {
            "localreport": None,
            "name": None,
            "color": None,
            "termstart": datetime(2023, 5, 15),
            "termend": None,
            "weeks": 5,
            "building": org.find_building("Building3"),
            "requestors": org.find_user(email="requestor2@example.com"),
            "remail": "requestor2@example.com",
            "rname": None,
            "rphone": None,
            "diagnoses": None,
            "anddiagnoses": None,
            "head": None,
            "tail": None,
            "querytype": "perweek"
        }
        self.assertEqual(args, expected)

        # load sample config 2
        args: dict = {"config": "unit-testing/expected-config2.json"}
        load_config(args)
        clean_args(args, org)
        # ensure it matches expected args dict
        expected: dict = {
            "localreport": "unit-testing/querytests1.csv",
            "name": "Cable Problems by Requestor",
            "color": "blue",
            "termstart": datetime(2023, 4, 4),
            "termend": datetime(2023, 6, 16),
            "weeks": None,
            "building": None,
            "remail": None,
            "rname": None,
            "rphone": None,
            "diagnoses": ["Cable--HDMI", "Cable-Ethernet"],
            "anddiagnoses": None,
            "head": 3,
            "tail": None,
            "querytype": "perrequestor"
        }
        self.assertEqual(args, expected)

        # using a different report
        report: Report = Report("unit-testing/minimal.csv")
        org: Organization = Organization()
        report.populate(org)

        # test that user-provided args replace json args
        args = {
            "config": "unit-testing/expected-config2.json",
            "localreport": "unit-testing/minimal.csv",
            "name": "",  # user can pass empty quotes for None
            "color": "red",
            "termstart": None,  # None means leave the json arg untouched
            "termend": "",
            "weeks": 10,
            "building": "The Building",
            "remail": None,
            "rname": None,
            "rphone": None,
            "diagnoses": "",
            "anddiagnoses": "Projector, TV Display, Cable--HDMI",
            "head": 0,
            "tail": None,
            "querytype": "perweek"
        }
        expected = {
            "localreport": "unit-testing/minimal.csv",
            "name": None,
            "color": "red",
            "termstart": datetime(2023, 4, 4),
            "termend": None,
            "weeks": 10,
            "building": org.find_building("The Building"),
            "remail": None,
            "rname": None,
            "rphone": None,
            "diagnoses": None,
            "anddiagnoses": ["Projector", "TV Display", "Cable--HDMI"],
            "head": None,
            "tail": None,
            "querytype": "perweek"
        }
        load_config(args)
        clean_args(args, org)
        self.assertEqual(args, expected)


class TestReport(unittest.TestCase):
    """
    Test cases for report.py,
    Specifically the Report class.
    """

    def test_populate(self):
        """
        Test cases for populate() method.
        """
        org = Organization()
        report = Report("unit-testing/minimal.csv")
        report.populate(org)

        # all campus entities created
        group: Group = org.find_group("USS-Classrooms")
        self.assertTrue(group)
        requestor: User = org.find_user("example@example.com", "Sir Example", "5555555555")[0]
        self.assertTrue(requestor)
        department: Department = org.find_department("Based Department")
        self.assertTrue(department)
        building: Building = org.find_building("The Building")
        self.assertTrue(building)
        room: Room = org.find_room("The Building", "111")
        self.assertTrue(room)

        # assert ticket created well
        self.assertEqual(len(org.tickets), 1)
        tick: Ticket = org.tickets.get(12345678)
        self.assertTrue(tick)
        self.assertEqual(tick.id, 12345678)
        self.assertEqual(tick.responsible_group, group)
        self.assertEqual(tick.requestor, requestor)
        self.assertEqual(tick.department, department)
        self.assertEqual(tick.room, room)
        self.assertEqual(tick.room.building, building)
        self.assertEqual(tick.created, datetime(2023, 7, 14, 10, 41))
        self.assertEqual(tick.modified, datetime(2023, 7, 14, 10, 41))
        # FIXME change to Enum once status functionality implemented
        self.assertEqual(tick.status, "Closed")

        # ticket lists for entities created well
        self.assertEqual(requestor.tickets, [tick])
        self.assertEqual(room.tickets, [tick])
        self.assertEqual(department.tickets, [tick])
        self.assertEqual(group.tickets, [tick])

    def test_dict_to_ticket(self):
        """
        Test cases for dict_to_ticket() method.
        """
        # setup
        # minimal.csv irrelevant to this test, passing to avoid error
        report = Report("unit-testing/minimal.csv")
        org = Organization()
        ticket_dict: dict = {"ID": "12345678",
                             "Title": "My Ticket",
                             "Resp Group": "USS-Classrooms",
                             "Requestor": "Sir Example",
                             "Requestor Email": "example@example.com",
                             "Requestor Phone": "5555555555",
                             "Acct/Dept": "Based Department",
                             "Location": "The Building",
                             "Location Room": "111",
                             "Classroom Problem Types": "Cable--HDMI, Touch Panel",
                             "Created": "7/14/2023 10:41",
                             "Modified": "7/14/2023 10:41",
                             "Status": "Closed"}

        ticket: Ticket = report.dict_to_ticket(org, ticket_dict)
        expected = [(ticket.room, org.find_room("The Building", "111")),
                    (ticket.responsible_group, org.find_group("USS-Classrooms")),
                    (ticket.requestor, org.find_user("example@example.com")[0]),
                    (ticket.department, org.find_department("Based Department"))]

        for pair in expected:
            self.assertEqual(pair[0], pair[1])

        # test for old building and room identifier names from TDX
        old_nomenclature_dict: dict = {
                             "Class Support Building": "Another Building",
                             "Room number": "99",
                             }

        ticket = report.dict_to_ticket(org, old_nomenclature_dict)
        self.assertEqual(ticket.room, org.find_room("Another Building", "99"))

        # test that old nomenclature not used if new nomenclature present
        mixed_nomenclature_dict: dict = {
            "Class Support Building": "Incorrect Building",
            "Room number": "50",
            "Location": "Correct Building",
            "Location Room": "100",
        }

        ticket = report.dict_to_ticket(org, mixed_nomenclature_dict)
        self.assertEqual(ticket.room, org.find_room("Correct Building", "100"))

    def test_constructor(self):
        """
        Test cases for __init__() constructor.
        """
        # ensure time_format and fields_present set well
        full_report: Report = Report("unit-testing/minimal.csv")
        self.assertEqual(full_report.fields_present,
                         ["id", "title", "responsible_group", "requestor_name", "requestor_email",
                          "requestor_phone", "department", "building", "room_identifier",
                          "diagnoses", "created", "modified", "status"])
        self.assertEqual(full_report.time_format, "%m/%d/%Y %H:%M")
        part_report: Report = Report("unit-testing/missing-fields.csv")
        self.assertEqual(part_report.fields_present, ["id", "title", "responsible_group", "department", "status"])
        self.assertEqual(part_report.time_format, None)

class TestVisual(unittest.TestCase):
    """
    Test cases for visual.py,
    Does not yet include test for graphing functions.
    """

    def test_crop_counts(self):
        """
        Test cases for crop_counts() method.
        """
        # setup
        source_labels: list[str] = ["label 5", "label 4", "label 3", "label 2", "label 1", "empty 1", "empty 2"]
        source_counts: list[str] = [5, 4, 3, 2, 1, 0, 0]
        cropped_labels: list[str]
        cropped_counts: list[int]

        # test for head
        args: dict = {"head": 6}
        expected_labels: list[str] = ["label 5", "label 4", "label 3", "label 2", "label 1", "empty 1"]
        expected_counts: list[str] = [5, 4, 3, 2, 1, 0]
        cropped_labels, cropped_counts = crop_counts(source_labels, source_counts, args)
        self.assertEqual(cropped_labels, expected_labels)
        self.assertEqual(cropped_counts, expected_counts)

        # test for tail
        args = {"tail": 4}
        expected_labels = ["label 2", "label 1", "empty 1", "empty 2"]
        expected_counts = [2, 1, 0, 0]
        cropped_labels, cropped_counts = crop_counts(source_labels, source_counts, args)
        self.assertEqual(cropped_labels, expected_labels)
        self.assertEqual(cropped_counts, expected_counts)

        # test for prune
        # specified by arg
        args = {"prune": True}
        expected_labels = ["label 5", "label 4", "label 3", "label 2", "label 1"]
        expected_counts = [5, 4, 3, 2, 1]
        cropped_labels, cropped_counts = crop_counts(source_labels, source_counts, args)
        self.assertEqual(cropped_labels, expected_labels)
        self.assertEqual(cropped_counts, expected_counts)

        # by length of labels
        source_labels = ["15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]
        source_counts = [0, 0, 0, 0, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        args = {}
        expected_labels = ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]
        expected_counts = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        cropped_labels, cropped_counts = crop_counts(source_labels, source_counts, args)
        self.assertEqual(cropped_labels, expected_labels)
        self.assertEqual(cropped_counts, expected_counts)

        # many labels but overriden by arg
        args = {"prune": False}
        cropped_labels, cropped_counts = crop_counts(source_labels, source_counts, args)
        self.assertEqual(cropped_labels, source_labels)
        self.assertEqual(cropped_counts, source_counts)

    def test_crop_tickets(self):
        """
        Test cases for crop_tickets() method.
        """
        # setup
        report: Report = Report("unit-testing/querytests1.csv")
        org: Organization = Organization()
        report.populate(org)
        source_list: list[Ticket] = [
            org.tickets[0],
            org.tickets[1],
            org.tickets[2],
            org.tickets[3],
            org.tickets[4],
            org.tickets[5],
            org.tickets[6],
            org.tickets[7],
            org.tickets[8],
            org.tickets[9]
        ]

        # test head
        args: dict = {"head": 5}
        expected_list: list[Ticket] = [
            org.tickets[0],
            org.tickets[1],
            org.tickets[2],
            org.tickets[3],
            org.tickets[4]
        ]
        cropped_list: list[Ticket] = crop_tickets(source_list, args)
        self.assertEqual(expected_list, cropped_list)

        # test tail
        args: dict = {"tail": 4}
        expected_list: list[Ticket] = [
            org.tickets[6],
            org.tickets[7],
            org.tickets[8],
            org.tickets[9]
        ]
        cropped_list: list[Ticket] = crop_tickets(source_list, args)
        self.assertEqual(expected_list, cropped_list)


if __name__ == "__main__":
    try:
        dir_test: typing.TextIO = open("unit-testing/context.py", mode="r", encoding="utf-8-sig")
        dir_test.close()
    except OSError:
        raise Exception("Run unit tests from project root, not from unit-testing dir")
    unittest.main()
