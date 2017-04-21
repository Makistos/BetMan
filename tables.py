import db_helpers as dbh
import arg_helper
import argparse
from prettytable import PrettyTable
import pprint

row_contents = lambda x: [x['Team'], x['W'] + x['D'] + x['L'], x['W'], x['D'], x['L'], x['GF'], x['GA'], x['GF'] - x['GA'], x['Pts']]
sorted_table = lambda tbl: sorted([x for x in tbl.values()], key=lambda y: (y['Pts'], y['GD']), reverse=True)


def __print_league_table(table):
    pretty = PrettyTable(['Team', 'Played', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts'])
    map(lambda x: pretty.add_row(row_contents(x)), table)
    print(pretty.get_string())

team_matches = lambda matches, name: [x for x in matches if x['home_name'] == name
                                      or x['away_name'] == name]
team_home_matches = lambda matches, name: [x for x in matches if x['home_name'] == name]
team_away_matches = lambda matches, name: [x for x in matches if x['away_name'] == name]
goals_for = lambda matches, name: sum([x['home_goals'] for x in matches
                                       if x['home_name'] == name]) \
                                  + sum([x['away_goals'] for x in matches
                                         if x['away_name'] == name])
goals_against = lambda matches, name: sum([x['home_goals'] for x in matches
                                           if x['away_name'] == name]) \
                                          + sum([x['away_goals'] for x in matches
                                                 if x['home_name'] == name])
wins = lambda matches, name: len([x for x in matches
                                  if (x['home_name'] == name
                                      and x['home_goals'] > x['away_goals'])
                                  or (x['away_name'] == name
                                      and x['away_goals'] > x['home_goals'])])
draws = lambda matches, name: len([x for x in matches
                                   if (x['home_name'] == name
                                       or x['away_name'] == name)
                                   and x['home_goals'] == x['away_goals']])
losses = lambda matches, name: len([x for x in matches
                                    if (x['home_name'] == name
                                        and x['home_goals'] < x['away_goals'])
                                    or (x['away_name'] == name
                                        and x['away_goals'] < x['home_goals'])])
team_form = lambda matches, name: { 'Team': name,
                       'W': wins(matches, name),
                       'D': draws(matches, name),
                       'L': losses(matches, name),
                       'GF': goals_for(matches, name),
                       'GA': goals_against(matches, name),
                       'GD': goals_for(matches, name) - goals_against(matches, name),
                       'Pts': 3 * wins(matches, name) + draws(matches, name)}


def __league_table(teams, matches):
    table = {}
    for team in teams:
        name = team['short_name']
        table[name] = team_form(matches, name)

    return sorted_table(table)


def league_table_season(conn, season):
    matches = dbh.matches_for_season(conn, season)
    teams = dbh.teams_for_season(conn, season)
    return __league_table(teams, matches)


def form_table(conn, date, sample=6, venue=None):
    """
    Returns an ordered form table with sample (default 6) size form table.

    :param conn: Open db connection.
    :param date: Date to generates the form table.
    :param sample: "Length" of form table, i.e. how many matches are counted
    backwards from date.
    :param venue: None, "Home" or "Away" - which matches to include.
    :return: Ordered form table (can be printed with __print_league_table()).
    """
    season = dbh.season_by_date(conn, date)
    teams = dbh.teams_for_season(conn, season)
    matches = list(reversed(dbh.matches_to_date(conn, season, date)))
    if venue == 'Home':
        forms = {x['short_name']:
                     team_form(team_home_matches(matches, x['short_name'])[0:sample], x['short_name'])
                 for x in teams}
    elif venue == 'Away':
        forms = {x['short_name']:
                     team_form(team_away_matches(matches, x['short_name'])[0:sample], x['short_name'])
                 for x in teams}
    else:
        forms = {x['short_name']:
                     team_form(team_matches(matches, x['short_name'])[0:sample], x['short_name'])
                 for x in teams}

    return sorted_table(forms)


def form_team(conn, team, date, sample=6, venue=None):
    season = dbh.season_by_date(conn, date)
    matches = tuple(reversed(dbh.matches_for_season(conn, season)))
    return team_form(team_matches(matches, team)[0:sample], team)


def form_table_between(conn, start_date, end_date):
    season = dbh.season_by_date(conn, start_date)
    teams = dbh.teams_for_season(conn, season)
    matches = dbh.matches_between(conn, start_date, end_date)
    return __league_table(teams, matches)


def main():
    parser = argparse.ArgumentParser(epilog=
                                     '''
                                     Commands: 1 = get league table for season (db_file, season)
                                     2 = get form table (db_file, season, location, date, count)
                                     ''')
    arg_helper.default_args(parser, True)
    parser.add_argument('-l', '--location', help='Venue (home/away)', default=None)
    parser.add_argument('-n', '--count', help='Match count', type=int)
    args = parser.parse_args()

    conn = dbh.create_connection(args.database)

    if args.command == 1:
        __print_league_table(league_table_season(conn, args.season))
    elif args.command == 2:
        __print_league_table(form_table(conn=conn, date=args.date, venue=args.location, sample=args.count))


if __name__ == "__main__":
    main()