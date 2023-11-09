"""
Ticket Report for tstat
by Eric Edwards, Alex JPS
2023-06-30

Report class and methods for parsing and populating tickets
from the information in a given report.
"""

# Packages
import sys
import csv
import typing
import json

# Files
from organization import *
from ticketclasses import *

# Constants

# match attribute names to TDX Academic Units Form names
STANDARD_FIELDS: dict[str, list[str]] = {
    "id": ["ID"],
    "title": ["Title"],
    "responsible_group": ["Resp Group"],
    "requestor_name": ["Requestor"],
    "requestor_email": ["Requestor Email"],
    "requestor_phone": ["Requestor Phone"],
    "department": ["Acct/Dept"],
    "building": ["Location", "Class Support Building"],
    "room_identifier": ["Location Room", "Room number"],
    "diagnoses": ["Classroom Problem Types"],
    "created": ["Created"],
    "modified": ["Modified"],
    "status": ["Status"]
}

TIME_FORMATS: list[str] = [
    # 12 hour
    "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M", "%m/%d/%y %H:%M", "%d.%m.%Y %H:%M", "%d.%m.%y %H:%M",
    # 24 hour
    "%Y-%m-%d %I:%M %p", "%m/%d/%Y %I:%M %p", "%m/%d/%y %I:%M %p", "%d.%m.%Y %I:%M %p", "%d.%m.%y %I:%M %p"
]


class BadReportError(ValueError):
    """
    Exception class for errors from bad report.
    Currently extends ValueError.
    """
    pass


class Report:
    """
    Class for the given report and its properties.
    Deals with file I/O and reading CSV.
    """
    time_format: str
    fields_present: list[str]
    filename = str
    diagnoses_aliases_filename = str

    def __init__(self, filename: str, diagnoses_aliases_filename: str = None):
        """
        Set attributes fields_present and time_format.
        Args should be confirmed valid files before passing.

        Parameters
        ----------
        filename:
            Filename for CSV local report
        diagnoses_filename:
            Optional JSON filename mapping aliases to diagnoses names
        """
        self.filename = filename
        self.diagnoses_aliases_filename = diagnoses_aliases_filename if diagnoses_aliases_filename else None

        # set fields present and time format
        csv_file: typing.TextIO = open(self.filename, mode="r", encoding="utf-8-sig")
        any_ticket: dict = next(csv.DictReader(csv_file))
        self.fields_present = get_fields_present(any_ticket)
        self.time_format = get_time_format(any_ticket)
        csv_file.close()

    def populate(self, org: Organization) -> None:
        """
        Given filename, read CSV.
        Populate buildings, rooms, tickets, etc. of given Organization.
        """
        csv_file: typing.TextIO = open(self.filename, mode="r", encoding="utf-8-sig")
        csv_tickets: csv.DictReader = csv.DictReader(csv_file)
        count: int = 0
        for row in csv_tickets:
            # fix row to be a valid, clean ticket dict
            new_ticket: Ticket = self.dict_to_ticket(org, row)
            org.add_new_ticket(new_ticket)
            count += 1
        csv_file.close()
        if not count:
            raise BadReportError("Ticket report is empty, exiting...")

    def dict_to_ticket(self, org: Organization, csv_ticket: dict) -> Ticket:
        """
        Given a dict representing a CSV row, convert to valid ticket.
        This does not add the ticket to the org's tickets dict,
        Nor does it add the ticket ot the on-campus entities' ticket lists.
        """

        def get_attribute(attribute_name: str) -> Union[str, None]:
            """
            Return the desired attribute for the given csv_ticket.
            Returns string as stored in CSV or None if empty.
            """
            for column_name in STANDARD_FIELDS[attribute_name]:
                if csv_ticket.get(column_name):
                    return csv_ticket[column_name]
            return None

        def gen_diagnoses() -> set[str]:
            """
            Return set of diagnoses for the ticket being created using
            diagnoses display names from diagnoses aliases file (if any).
            File from self.diagnoses_aliases_filename expected valid.
            """
            # get diagnoses field from csv_ticket
            diagnoses_field: str = get_attribute("diagnoses")

            # return empty set if nothing from diagnoses field
            if not diagnoses_field:
                return set()

            # canonize and split string into list
            canonized_diagnoses_field: str = "".join(
                char for char in diagnoses_field.lower() if char.isalpha() or char == ","
            )
            diagnoses_list: list[str] = canonized_diagnoses_field.split(",")

            # if alias mappings provided, replace with display names
            if not self.diagnoses_aliases_filename:
                return set(diagnoses_list)
            # diagnoses aliases file present, so replace diagnoses values with display names
            aliases_file: typing.TextIO = open(self.diagnoses_aliases_filename, mode="r", encoding="utf-8-sig")
            alias_mappings: dict[str, str] = json.load(aliases_file)
            for i in range(len(diagnoses_list)):
                if alias_mappings.get(diagnoses_list[i]):
                    diagnoses_list[i] = alias_mappings[diagnoses_list[i]]
            aliases_file.close()
            return set(diagnoses_list)

        # new ticket
        new_ticket: Ticket = Ticket()

        # set title attribute
        new_ticket.title = get_attribute("title")

        # use find methods set OrganizationEntity objects
        new_ticket.responsible_group = org.find_group(get_attribute("responsible_group"), create_mode=True)
        new_ticket.department = org.find_department(get_attribute("department"), create_mode=True)
        new_ticket.room = org.find_room(get_attribute("building"),
                                        get_attribute("room_identifier"), create_mode=True)
        # some extra steps for Requestor because find_user() takes multiple args
        # pass "Undefined" for blanks so no "partial matches" (e.g. same email but missing name)
        requestor_email: str = get_attribute("requestor_email") if get_attribute("requestor_email") else "Undefined"
        requestor_name: str = get_attribute("requestor_name") if get_attribute("requestor_name") else "Undefined"
        requestor_phone: str = get_attribute("requestor_phone") if get_attribute("requestor_email") else "Undefined"
        requestor_lookup: list[User] = org.find_user(requestor_email, requestor_name, requestor_phone, create_mode=True)
        # make sure only 1 user is returned on find_user()
        if len(requestor_lookup) != 1:
            raise ValueError("""Multiple or no requestor objects found for one ticket in populate() method
Possible bad usage of find_user() method""")
        assert isinstance(requestor_lookup[0], User)
        new_ticket.requestor = requestor_lookup[0]

        # ID should be an int
        id_attribute: str = get_attribute("id")
        new_ticket.id = int(id_attribute) if id_attribute else 0

        # Created and Modified should be datetime objects
        created_attribute: str = get_attribute("created")
        new_ticket.created = datetime.strptime(created_attribute, self.time_format) if created_attribute else None
        modified_attribute: str = get_attribute("modified")
        new_ticket.modified = datetime.strptime(modified_attribute, self.time_format) if modified_attribute else None

        # diagnoses attribute should be list of valid diagnoses strings
        new_ticket.diagnoses = gen_diagnoses()

        # FIXME change to Enum once status functionality implemented
        new_ticket.status = get_attribute("status")

        # return finished ticket
        return new_ticket

# Helper functions

def get_fields_present(csv_ticket: dict) -> Union[list[str], None]:
    """
    Given an arbitrary csv_ticket dict from report,
    Check which of STANDARD_FIELDS are present in report.
    Set self.fields_present accordingly.
    """
    # return variable
    fields_present: list[str] = []

    # for determining what warnings to show
    legacy_fields: list[tuple[str, str]] = []
    missing_fields: list[str] = []

    # loop through attribute names
    for attribute in STANDARD_FIELDS.keys():
        # ensure one of attribute's column names present in report
        attribute_present: bool = False
        for csv_column_name in STANDARD_FIELDS[attribute]:
            # check if attribute found using this CSV column name
            if csv_ticket.get(csv_column_name) is not None:
                attribute_present = True
                fields_present.append(attribute)
                # check if it is a legacy field so we can warn later
                if csv_column_name != STANDARD_FIELDS[attribute][0]:
                    legacy_fields.append((csv_column_name, STANDARD_FIELDS[attribute][0]))
        # if none of acceptable column names found, attribute missing
        if not attribute_present:
            missing_fields.append(attribute)

    # general guidelines warning
    if missing_fields or legacy_fields:
        print("Report does not follow tdxplot Standard Report Guidlines. See issues below:", file=sys.stderr)

    # warn of legacy names
    for pair in legacy_fields:
        print(f"Report uses legacy field \"{pair[0]}\". New convention is \"{pair[1]}\"", file=sys.stderr)

    # warn of missing fields
    for field in missing_fields:
        print(f"Report is missing field \"{STANDARD_FIELDS[field][0]}\"")

    return fields_present


def get_time_format(csv_ticket: dict) -> Union[str, None]:
    """
    Given an arbitrary csv_ticket dict from report,
    Check that time adheres to one of TIME_FORMATS.
    Returns format string or throws error if no match.
    """
    # check whether a time attribute is present
    if csv_ticket.get("Created"):
        time_text: str = csv_ticket["Created"]
    elif csv_ticket.get("Modified"):
        time_text: str = csv_ticket["Modified"]
    else:
        # no date attributes, so no time format to set
        return None
    for try_format in TIME_FORMATS:
        try:
            datetime.strptime(time_text, try_format)
            return try_format
        except ValueError:
            continue
    raise BadReportError(f"Time {time_text} in report is not a valid time format")
