"""
Data Visualization for tdxplot
by Alexa Roskowski, Alex JPS
2023-07-06

Takes dictionary from an Organization query method,
Visualizes the data in appropriate format.
"""

# import libraries
from datetime import *
import io
from matplotlib import pyplot

# constants
DEFAULT_COLOR = "gray"
DEFAULT_NAMES = {"perweek": "Tickets per Week",
                 "perbuilding": "Tickets per Building",
                 "perroom": "Tickets per Room",
                 "perrequestor": "Tickets per Requestor"}

def view_per_week(tickets_per_week: dict[datetime, int], args: dict) -> None:
    """
    Display bar chart showing ticket counts per week.
    """
    # sort keys
    if args.get("head") or args.get("tail"):
        # sort by count
        sorted_counts = sorted(tickets_per_week.items(), key=lambda item: item[1], reverse=True)

    else:
        # sort temporally
        weeks: list[datetime] = list(tickets_per_week.keys())
        weeks.sort()
        week_counts: list[int] = [tickets_per_week[week] for week in weeks]

    week_labels: list[str] = []
    for i in range(len(weeks)):
        label = f"""W{i+1}\n{datetime.strftime(weeks[i], "%m/%d")}"""
        if i == 0:
            label += f"""\n{datetime.strftime(weeks[i], "%Y")}"""
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

def bar_view(bar_labels: list[str], bar_heights: list[int], args: dict) -> None:
    """
    Display a bar chart using given bar labels and bar heights.
    Applies cosmetic changes from args.
    """
    # crop bars
    bar_labels, bar_heights = crop_counts(bar_labels, bar_heights, args)

    # initialize the graph
    fig, ax = pyplot.subplots(figsize=(10, 5))
    color: str = args["color"] if args.get("color") else DEFAULT_COLOR
    ax.bar(bar_labels, bar_heights, color=args.get("color"))

    # pyplot.xlabel("Weeks") # removed cause each bar is labeled Week (num)
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
            horizontalalignment = "center",
            verticalalignment = "bottom",
            color = "Black",
            fontsize = "medium"
        )

    if args["querytype"] in ["perbuilding", "perroom", "perrequestor"]:
        # adjust for long building names
        # FIXME take in building name abbreviations
        pyplot.xticks(rotation=45, ha='right')
        pyplot.subplots_adjust(bottom=0.25)

    pyplot.show()

def crop_counts(labels: list[str], counts: list[int], args) -> tuple[list[str], list[int]]:
    """
    Crop counts based on "head" and "tail" values in args.
    No sorting here. Preserves elements order given in arrays,
    Although other funcs may sort differently on "head"/"tail".
    """
    if args.get("head") is None and args.get("tail") is None:
        return labels, counts
    if args.get("head"):
        return labels[:args["head"]], counts[:args["head"]]
    if args.get("tail"):
        return labels[-args["tail"]:], counts[-args["tail"]:]