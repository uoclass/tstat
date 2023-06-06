"""
Command-line interface for tdxplot
by Eric Edwards, Alex JPS
2023-06-06

The primary .py file form which the program should run.
Parses user input via command-line arguments.
Passes a dictionary with info to appropriate files or functions.
"""

import argparse
import plot


def main():
    colors = ['white', 'black', 'gray', 'yellow', 'red', 'blue', 'green', 'brown', 'pink', 'orange', 'purple'] 
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub_command help')

    parser_set_info = subparsers.add_parser('set_info', help='the set_info command allows setting of the graph name')
    parser.add_argument('-n', '--name', type=str, help='Set the name of the plot.')
    parser.add_argument('-c', '--color', choices=colors, help='Set the color of the plot.')
    parser.add_argument('-i', '--input', type=str, help='Set the filename from which CSV info is pulled.')

    args = parser.parse_args()

    args_dict = vars(args)

    # call plot tool
    print(args_dict)
    plot.ticketCountPerTerm(args_dict)


if __name__ == "__main__":
    main()