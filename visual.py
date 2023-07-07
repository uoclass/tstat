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
                 "perroom": "Tickets per Room"}

def view_per_week(tickets_per_week: dict[datetime, int], args: dict) -> None:
    """
    Display graph showing ticket counts per week.
    """
    # sort keys
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


def bar_view(bar_labels: list[str], bar_heights: list[int], args: dict) -> None:
    """
    Display a bar chart using given bar labels and bar heights.
    Applies cosmetic changes from args.
    """
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

    pyplot.show()
