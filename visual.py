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

    # initialize the graph
    fig, ax = pyplot.subplots(figsize=(10, 5))
    if args.get("color"):
        ax.bar(week_labels, week_counts, color=args.get("color"))
    else:
        ax.bar(week_labels, week_counts, color="green")

    # pyplot.xlabel("Weeks") # removed cause each bar is labeled Week (num)
    ax.set_ylabel("Count")
    if args.get("name"):
        ax.set_title(args.get("name"))
    else:
        ax.set_title("Number of Tickets Per Week")

    rect = ax.patches
    for rect, c in zip(rect, week_counts):
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
