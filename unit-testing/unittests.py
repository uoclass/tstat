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
        """
        org = Organization()
        # Example valid ticket dict
        ticket_dict = {"ID": 1111111, "Title": "Test fake ticket.",
                       "Resp Group": "USS-Classrooms",
                       "Requestor": "Eric",
                       "Requestor Email": "ee@uoregon.edu",
                       "Requestor Phone": "5305305303",
                       "Acct/Dept": "Computer Science",
                       "Class Support Building": "Lawrence",
                       "Room number": "177",
                       "Created": datetime(2022, 7, 10, 9, 38),
                       "Modified": datetime(2022, 7, 11, 11, 53),
                       "Status": "Closed"}

        org.add_new_ticket(ticket_dict)

        # Ticket added to org ticket dict
        self.assertTrue(isinstance(org.tickets[1111111], Ticket))

        # Ticket attributes properly set
        curr = org.tickets[1111111]
        self.assertEqual(1111111, curr.id)
        self.assertEqual("Test fake ticket.", curr.title)
        self.assertEqual("Eric", curr.requestor.name)
        self.assertEqual("ee@uoregon.edu", curr.requestor.email)
        self.assertEqual("5305305303", curr.requestor.phone)
        self.assertEqual("Computer Science", curr.department.name)
        self.assertEqual("Lawrence", curr.room.building.name)
        self.assertEqual("177", curr.room.identifier)
        self.assertEqual(datetime(2022, 7, 10, 9, 38), curr.created)
        self.assertEqual(datetime(2022, 7, 11, 11, 53), curr.modified)
        # self.assertEqual(0, curr.status)

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

        # returns None for nonexistent user
        no_user: User = org.find_user("realemail@email.net", "AJ", "541541541")
        self.assertEqual(no_user, None)

        # returns and adds new user when create_mode
        new_user: User = org.find_user("realemail@email.net", "AJ", "541541541", create_mode=True)
        self.assertTrue(isinstance(new_user, User))
        self.assertEqual(new_user, org.users["realemail@email.net"])
        self.assertEqual(new_user.email, "realemail@email.net")
        self.assertEqual(new_user.name, "AJ")
        self.assertEqual(new_user.phone, "541541541")

        # "Undefined" attributes when omitted
        empty_user: User = org.find_user(create_mode=True)
        self.assertEqual(empty_user.email, "Undefined")
        self.assertEqual(empty_user.name, "Undefined")
        self.assertEqual(empty_user.phone, "Undefined")

        # "Undefined" attributes when None passed
        none_user: User = org.find_user(None, None, None, create_mode=True)
        self.assertEqual(none_user.email, "Undefined")
        self.assertEqual(none_user.name, "Undefined")
        self.assertEqual(none_user.phone, "Undefined")

        # returns existing user now
        my_user: User = org.find_user("realemail@email.net")
        self.assertEqual(my_user, new_user)

        # also works with name or phone or both
        my_user = org.find_user(name="AJ")
        self.assertEqual(my_user, new_user)
        my_user = org.find_user(phone="541541541")
        self.assertEqual(my_user, new_user)
        my_user = org.find_user(None, "AJ", "541541541")
        self.assertEqual(my_user, new_user)

        # still returns existing group when create_mode
        same_user: User = org.find_user("realemail@email.net", create_mode=True)
        self.assertEqual(same_user, new_user)

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

    def test_get_modnay(self):
        """
        Test cases for get_monday() helper function.
        """
        self.assertEqual(get_monday(datetime(2023, 7, 27),), datetime(2023, 7, 24))
        self.assertEqual(get_monday(datetime(2023, 6, 26),), datetime(2023, 6, 26))
        self.assertEqual(get_monday(datetime(2023, 7, 23),), datetime(2023, 7, 17))

    def test_filter_tickets(self):
        """
        Test cases for filter_tickets() helper function.
        """
        # set up
        report = Report("unit-testing/querytests1.csv")
        org = Organization()
        report.populate(org)
        args: dict = {
            "termstart": datetime(2023, 4, 11),
            "termend": datetime(2023, 5, 29),
            "building": org.find_building("Building3"),
            "requestor": org.find_user("requestor1@example.com")
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
            # update the exclude list below once more filters added
            filtered: list[Ticket] = filter_tickets(type, args, ["building", "requestor"])
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
            # update the exclude list below once more filters added
            filtered: list[Ticket] = filter_tickets(type, args, ["termstart", "termend", "requestor"])
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
            # update the exclude list below once more filters added
            filtered: list[Ticket] = filter_tickets(type, args, ["requestor"])
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
            # update the exclude list below once more filters added
            filtered: list[Ticket] = filter_tickets(type, args, ["termend", "termstart", "building"])
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
        args = {"termend": datetime(2023, 6, 29), "requestor": org.find_user("requestor2@example.com")}
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
        args = {"requestor": org.find_user("requestor1@example.com")}
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
        args = {"requestor": org.find_user("requestor1@example.com")}
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
        requestor1: User = org.find_user("requestor1@example.com")
        requestor2: User = org.find_user("requestor2@example.com")
        requestor3: User = org.find_user("requestor3@example.com")

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
        args = {"termstart": datetime(2023, 4, 20), "termend": datetime(2023, 5, 27), "building": org.find_building("Building2")}
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
        Ensure traceback is changed by -d flag.
        """
        argv: list[str] = ["-d", "--perweek", "--nographics", "unit-testing/minimal.csv"]
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
        argv: list[str] = ["--perweek", "unit-testing/no-file.csv"]
        self.assertRaises(BadArgError, main, argv)
        argv = ["--perweek", "unit-testing/not-a-csv.txt"]
        self.assertRaises(BadArgError, main, argv)
        argv = ["--perweek"]
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
        argv: list[str] = ["-d", "--nographics", "--perweek", "-t", "19700101", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

    def test_set_query_type(self):
        """
        Test cases for set_query_type() function.
        """
        # dict gets modified
        args: dict = {"perweek": True}
        set_query_type(args)
        self.assertEqual(args["querytype"], "perweek")

        # rejects multiple types
        args: dict = {"perweek": True, "perbuilding": True}
        self.assertRaises(BadArgError, set_query_type, args)


    def test_check_options(self):
        """
        Test cases for check_options() function.
        Tests main(argv) rather than check_options() directly.
        """
        # debug stipulations (pass --nographics without -d)
        argv: list[str] = ["--nographics", "--perweek", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

        # perbuilding stipulations (pass -b with --perbuilding)
        argv = ["-d", "--nographics", "--perbuilding", "-b", "Lillis", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

        # perweek stipulations
        # pass -w without --perweek
        argv = ["--perbuilding", "-w", "10", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)
        # pass -w and -e at once
        argv = ["--perweek", "-w", "10", "-e", "12/31/2023", "unit-testing/minimal.csv"]
        self.assertRaises(BadArgError, main, argv)

        # perrequestor stipulations
        args = {"--perrequestor", "--requestor", "requestor1@example.com", "unit-testing/minimal.csv"}
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
        requestor: User = org.find_user("example@example.com", "Sir Example", "5555555555")
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
        self.assertEqual(tick.responsible, group)
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

    def test_clean_ticket_dict(self):
        """
        Test cases for clean_ticket_dict() method.
        """
        # ensure cleaned dict matches expectation
        report = Report("unit-testing/minimal.csv")
        dirty_dict: dict = {"ID": "12345678",
                            "Title": "My Ticket",
                            "Resp Group": "USS-Classrooms",
                            "Requestor": "Sir Example",
                            "Requestor Email": "example@example.com",
                            "Requestor Phone": "5555555555",
                            "Acct/Dept": "Based Department",
                            "Class Support Building": "The Building",
                            "Room number": "111",
                            "Classroom Problem Types": "Cable--HDMI, Touch Panel",
                            "Created": "7/14/2023 10:41",
                            "Modified": "7/14/2023 10:41",
                            "Status": "Closed"}
        expected: dict = {"ID": 12345678,
                          "Title": "My Ticket",
                          "Resp Group": "USS-Classrooms",
                          "Requestor": "Sir Example",
                          "Requestor Email": "example@example.com",
                          "Requestor Phone": "5555555555",
                          "Acct/Dept": "Based Department",
                          "Class Support Building": "The Building",
                          "Room number": "111",
                          "Classroom Problem Types": [Diagnosis.CABLE_HDMI, Diagnosis.TOUCH_PANEL],
                          "Created": datetime(2023, 7, 14, 10, 41),
                          "Modified": datetime(2023, 7, 14, 10, 41),
                          "Status": "Closed"}
        report.clean_ticket_dict(dirty_dict)
        self.assertEqual(dirty_dict, expected)

    def test_constructor(self):
        """
        Test cases for __init__() constructor.
        """
        # ensure time_format and fields_present set well
        full_report: Report = Report("unit-testing/minimal.csv")
        self.assertEqual(full_report.fields_present, ["ID", "Title", "Resp Group", "Requestor", "Requestor Email",
                                                 "Requestor Phone", "Acct/Dept", "Class Support Building",
                                                 "Room number", "Classroom Problem Types", "Created", "Modified", "Status"])
        self.assertEqual(full_report.time_format, "%m/%d/%Y %H:%M")
        part_report: Report = Report("unit-testing/missing-fields.csv")
        self.assertEqual(part_report.fields_present, ["ID", "Title", "Resp Group", "Acct/Dept", "Status"])
        self.assertEqual(part_report.time_format, None)

if __name__ == "__main__":
    try:
        dir_test: typing.TextIO = open("unit-testing/context.py", mode="r", encoding="utf-8-sig")
        dir_test.close()
    except OSError:
        raise Exception("Run unit tests from project root, not from unit-testing dir")
    unittest.main()
