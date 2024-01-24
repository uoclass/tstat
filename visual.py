"""
Data Visualization for tstat
by Alexa Roskowski, Alex JPS
2023-07-06

Takes dictionary from an Organization query method,
Visualizes the data in appropriate format.
"""

# import libraries
from datetime import *
import io
from matplotlib import pyplot
from ticketclasses import *

# constants
DEFAULT_COLOR = "gray"
DEFAULT_NAMES = {"perweek": "Tickets per Week",
                 "perbuilding": "Tickets per Building",
                 "perroom": "Tickets per Room",
                 "perrequestor": "Tickets per Requestor"}
PRUNE_COUNT = 15


def view_per_week(tickets_per_week: dict[datetime, int], args: dict) -> None:
    """
    Display bar chart showing ticket counts per week.
    """
    weeks: list[datetime]
    week_counts: list[int]
    # sort keys
    if args.get("head") or args.get("tail"):
        # sort by count, high to low
        sorted_counts = sorted(tickets_per_week.items(), key=lambda item: item[1], reverse=True)
        weeks = [item[0] for item in sorted_counts]
        week_counts = [item[1] for item in sorted_counts]
    else:
        # sort temporally
        weeks = list(tickets_per_week.keys())
        weeks.sort()
        week_counts = [tickets_per_week[week] for week in weeks]

    week_labels: list[str] = []
    first_week = min(weeks)
    for week in weeks:
        week_num: int = (week - first_week).days // 7 + 1
        label = f"""W{week_num}\n{datetime.strftime(week, "%m/%d")}"""
        week_labels.append(label)

    bar_view(week_labels, week_counts, args)


def view_per_building(tickets_per_building: dict["Building", int], args: dict) -> None:
    """
    Display bar chart showing ticket counts per building.
    """
    building_labels: list[str] = []
    building_counts: list[int] = []
    sorted_counts = sorted(tickets_per_building.items(), key=lambda item: item[1], reverse=True)
    for building, count in sorted_counts:
        building_labels.append(building.name)
        building_counts.append(count)

    bar_view(building_labels, building_counts, args)


def view_per_room(tickets_per_room: dict["Room", int], args: dict) -> None:
    """
    Display bar chart showing ticket counts per room.
    """
    room_labels: list[str] = []
    room_counts: list[int] = []
    sorted_counts = sorted(tickets_per_room.items(), key=lambda item: item[1], reverse=True)
    for room, count in sorted_counts:
        room_label = f"{room.building.name} {room.identifier}"
        room_labels.append(room_label)
        room_counts.append(count)

    bar_view(room_labels, room_counts, args)


def view_per_requestor(tickets_per_requestor: dict["User", int], args: dict) -> None:
    """
    Display bar chart showing ticket counts by requestor.
    """
    # FIXME: Finish
    requestor_labels: list[str] = []
    requestor_counts: list[int] = []
    sorted_counts = sorted(tickets_per_requestor.items(), key=lambda item: item[1], reverse=True)
    for requestor, count in sorted_counts:
        requestor_name = f"{requestor.name}"
        requestor_labels.append(requestor_name)
        requestor_counts.append(count)

    bar_view(requestor_labels, requestor_counts, args)


def view_show_tickets(tickets_matched: list["Ticket"], args: dict) -> None:
    """
    Print matched tickets.
    """
    # sort by date (newest to oldest)
    tickets_matched.sort(key=lambda ticket: ticket.created, reverse=True)
    # crop for head or tail args
    tickets_matched = crop_tickets(tickets_matched, args)
    # print remaining tickets
    print(f"Matching tickets ({len(tickets_matched)})")
    print("----------------")
    for ticket in tickets_matched:
        print(ticket)
        print("----------------")
    print(f"Matching tickets ({len(tickets_matched)})")


def bar_view(bar_labels: list[str], bar_heights: list[int], args: dict) -> None:
    """
    Display a bar chart using given bar labels and bar heights.
    Applies cosmetic changes from args.
    """
    # crop bars
    bar_labels, bar_heights = crop_counts(bar_labels, bar_heights, args)

    # differentiate duplicate labels to prevent matplotlib grouping them
    dupes: dict[str, int]= {}
    for i in range(len(bar_labels)):
        if not dupes.get(bar_labels[i]):
            dupes[bar_labels[i]] = 1
        else:
            dupes[bar_labels[i]] += 1
            bar_labels[i] = f"{bar_labels[i]} ({dupes[bar_labels[i]]})"

    # initialize the graph
    fig, ax = pyplot.subplots(figsize=(10, 5))
    color: str = args["color"] if args.get("color") else DEFAULT_COLOR
    ax.bar(bar_labels, bar_heights, color=args.get("color"))

    ax.set_ylabel("Count")
    if args.get("name"):
        ax.set_title(args["name"])
    else:
        ax.set_title(DEFAULT_NAMES[args["querytype"]])

    rect = ax.patches
    for rect, c in zip(rect, bar_heights):
        # add the count to the graph
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2,
            height + 0.01,
            c,
            horizontalalignment="center",
            verticalalignment="bottom",
            color="Black",
            fontsize="medium"
        )

    if args["querytype"] in ["perbuilding", "perroom", "perrequestor"]:
        # adjust for long building names
        # FIXME take in building name abbreviations
        pyplot.xticks(rotation=45, ha='right')
        pyplot.subplots_adjust(bottom=0.25)

    pyplot.show()


def crop_counts(labels: list[str], counts: list[int], args) -> tuple[list[str], list[int]]:
    """
    Crop counts based on head, tail, or prune in args.
    No sorting here. Preserves elements order given in arrays,
    Although other funcs may sort differently on "head"/"tail".
    """

    def prune_counts() -> tuple[list[str], list[int]]:
        pruned_labels: list[str] = []
        pruned_counts: list[str] = []
        for i in range(len(counts)):
            if counts[i] > 0:
                pruned_labels.append(labels[i])
                pruned_counts.append(counts[i])
        return pruned_labels, pruned_counts

    if args.get("head"):
        return labels[:args["head"]], counts[:args["head"]]
    if args.get("tail"):
        return labels[-args["tail"]:], counts[-args["tail"]:]
    if args.get("prune") or (len(counts) >= PRUNE_COUNT and args.get("prune") != False):
        # prune the graph by removing 0 counts
        return prune_counts()

    # no cropping
    return labels, counts


def crop_tickets(tickets: list["Ticket"], args) -> list["Ticket"]:
    """
    Crop a simple ticket list based on head or tail in args.
    """
    if args.get("head"):
        return tickets[:args["head"]]
    if args.get("tail"):
        return tickets[-args["tail"]:]

    # no cropping
    return tickets
