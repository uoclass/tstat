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
    Specifically the Organization class.
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


class TestCli(unittest.TestCase):
    """
    Test cases for command line interface in py.
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


    def test_bad_files(self):
        """
        Ensure a BadArgError results from a missing or non-CSV filename.
        """
        # missing file
        argv: list[str] = ["--perweek", "unit-testing/no-file.csv"]
        self.assertRaises(BadArgError, main, argv)

        # file exists but not CSV
        argv = ["--perweek", "unit-testing/not-a-csv.txt"]
        self.assertRaises(BadArgError, main, argv)


class TestReport(unittest.TestCase):
    """
    Test cases for the report.py,
    Specifically the Report class.
    """
    def test_populate(self):
        org = Organization()
        report = Report("unit-testing/minimal.csv")
        report.populate(org)
        
        # empty report
        org = Organization()
        report = Report("unit-testing/blanks.csv")
        report.populate(org)

        # all fields report
        # all incorrect fields report

if __name__ == "__main__":
    unittest.main()
