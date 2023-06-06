"""
Ticket Sorting and Plotting for tdxplot
by Alexa Roskowski, Alex JPS
2023-02-16

Takes dictionary of info called by cli.py.
Sorts tickets and displays graph from info in a CSV file from a TDX Report.
Report must at least contain Responsible Group and Modified.
"""

import csv  # used for reading the file
import os
from datetime import datetime, date  # used for sorting by modified date
import matplotlib.pyplot as plt  # used for plotting pretty graphs


def ticketCountPerTerm(args_dict):
    filecheck(args_dict.get('input'))
    f = open(args_dict.get('input'), mode='r')
    csv_reader = csv.DictReader(f)


    classroomTickets = []  # list of all the tickets where USS Classrooms are responsible
    for row in csv_reader:
        # loop through and check the responsible group
        if row['Resp Group'] == 'USS-Classrooms':
            # add to the list
            classroomTickets.append(row)

    f.close()  # we are done taking the important data from the csv file so close it

    # sort the tickets by the modified date
    classroomTickets.sort(key=lambda d: datetime.strptime(d['Modified'], "%m/%d/%Y %H:%M"))

    ticketPerWeek = [0] * 11  # list of the counts of tickets per week

    first_ticket = datetime.strptime(classroomTickets[0]['Modified'], "%m/%d/%Y %H:%M")

    for ticket in classroomTickets:
        # figure out which week the ticket is in
        date = datetime.strptime(ticket['Modified'], "%m/%d/%Y %H:%M")
        delta = date - first_ticket
        index = delta.days // 7
        # incase you pulled a date a little too far
        index = index - 1 if index >= 11 else index

        # add to the count of whcih week its in
        ticketPerWeek[index] += 1

    print(ticketPerWeek)

    # Refactor this to a separate graphing function or file
    weeks = ["Week " + str(i + 1) for i in range(11)]  # list of week count for graph
    # print(weeks)

    # initialize the graph
    fig, ax = plt.subplots(figsize=(10, 5))
    if args_dict.get('color'):
        ax.bar(weeks, ticketPerWeek, color=args_dict.get('color'))
    else:
        ax.bar(weeks, ticketPerWeek, color='green')

    # plt.xlabel("Weeks") # removed cause each bar is labeled Week (num)
    ax.set_ylabel("Count")
    if args_dict.get('name'):
        ax.set_title(args_dict.get('name'))
    else:
        ax.set_title("Number of Tickets Per Week")

    rect = ax.patches
    for rect, c in zip(rect, ticketPerWeek):
        # add the count to the graph
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2,
            height + 0.01,
            c,
            horizontalalignment='center',
            verticalalignment='bottom',
            color='Black',
            fontsize='medium'
        )

    plt.show()


def filecheck(filename: str):
    """
    Check that the given filename exists and is a CSV file.
    Check that the required fields are present.
    Return opened file
    """
    if not filename:
        print("No file input provided")
        exit(1)
    filename.strip()
    if not (os.path.exists(filename)):
        print("File input not found")
        exit(1)
    if (os.path.splitext(filename)[-1].lower()) != '.csv':
            print("Not a CSV file")
            exit(1)
    file = open(filename, mode='r')
    file_read = file.readlines()
    if not "Resp Group" in file_read[0]:
        print("File input does not contain Resp Group")
    if not "Modified" in file_read[0]:
        print("File input does not contain Modified")
    file.close()