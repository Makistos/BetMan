import argparse


def default_args(parser, db_required=False):
    if db_required:
        parser.add_argument('database', help='Database file')
    parser.add_argument('-c', '--command', help='Command to execute', type=int)
    parser.add_argument('-d', '--date', help='Date')
    parser.add_argument('-g', '--graphical', const=True, action='store_const', help='Graphical mode (limited)')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-s', '--season', help='Season')
    parser.add_argument('-t', '--team', help='Team name')
    parser.add_argument('-v', '--verbose', action='count', help='Output verbosity')
