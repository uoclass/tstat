import argparse

def setName():
    print("Setting name.")



def main(args):
    d = vars(args)

    # defaults
    color = 'blue'
    graphName = 'Ticket Plot'

    print(d)
    if d.get('color'): 
        color = d.get('color')
    print(color)


if __name__ == "__main__":
    colors = ['white', 'black', 'gray', 'yellow', 'red', 'blue', 'green', 'brown', 'pink', 'orange', 'purple'] 
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub_command help')

    parser_set_info = subparsers.add_parser('set_info', help='the set_info command allows setting of the graph name')
    parser_set_info.add_argument('-n', '--name', type=str, help='Set the name of the plot.')

    parser_set_visuals = subparsers.add_parser('set_vis', help='the set_vis command allows the modification of visual options')
    parser_set_visuals.add_argument('-c', '--color', choices=colors, help='Set the color of the plot.')
    args = parser.parse_args()

    main(args)
