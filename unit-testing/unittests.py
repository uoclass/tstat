"""
Unit Tests for tdxplot
by Eric Edwards, Alex JPS
2023-07-06

Unit testing for organization methods, i.e. filtering, sorting, adding / finding tickets.
"""

import context
from organization import *
from ticketclasses import *
from report import *
import unittest


class TestTicketclasses(unittest.TestCase):
    def setUp(self):
        self.org = Organization()

    def test_add_new_ticket(self):
        self.org.add_new_ticket({"ID": 1111111, "Title": "Test fake ticket.", 
                                 "Resp Group": "USS-Classrooms",
                                 "Requestor": "Eric", 
                                 "Requestor Email": "ee@uoregon.edu", 
                                 "Requestor Phone": "5305305303", 
                                 "Acct/Dept": "Computer Science", 
                                 "Class Support Building": "Lawrence", 
                                 "Room number": "177", 
                                 "Created": datetime(2022, 7, 10), 
                                 "Modified": datetime(2022, 7, 11), 
                                 "Status": "Closed"})
        curr = self.org.tickets[1111111]
        self.assertEqual(1111111, curr.id)
        self.assertEqual("Test fake ticket.", curr.title)
        self.assertEqual("Eric", curr.requestor.name)
        self.assertEqual("ee@uoregon.edu", curr.requestor.email)
        self.assertEqual("5305305303", curr.requestor.phone)
        self.assertEqual("Computer Science", curr.department.name)
        self.assertEqual("Lawrence", curr.room.building.name)
        self.assertEqual("177", curr.room.identifier)
        self.assertEqual(datetime(2022, 7, 10), curr.created)
        self.assertEqual(datetime(2022, 7, 11), curr.modified)
        # self.assertEqual(0, curr.status)


if __name__ == "__main__":
    unittest.main()