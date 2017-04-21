import sys
import sqlite3
import getopt
import arg_helper
import argparse
from enum import Enum
import pprint

MATCH_COLS = 'm.date, t1.short_name as home_name, t2.short_name as away_name, m.home_team, m.away_team,' \
             ' mth.GF as home_goals, mth.GA as away_goals, mth.matchno as home_matchno, mta.matchno as away_matchno'
MATCH_TABLES = 'match m, matchteam mth, matchteam mta, team t1, team t2'
MATCH_TABLE_LINKS = 'm.home_team = mth.id and m.away_team = mta.id and t1.id = mth.team and t2.id = mta.team'

class MatchTeam(Enum):
    ID = 0
    TEAM = 1
    GF = 2
    GA = 3
    VENUE = 4
    MATCHNO = 5
    MATCHNOV = 6


def __dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    conn.row_factory = __dict_factory
    return conn


# Functions for retrieving lists of matches based on different criteria.
# The result is a list of dicts consisting of fields in MATCH_COLS.
def matches_for_season(conn, season):
    c = conn.cursor()
    sql = 'SELECT DISTINCT ' + MATCH_COLS + \
          ' FROM ' + MATCH_TABLES + \
          ' WHERE ' + MATCH_TABLE_LINKS + \
          ' and m.season = ? ' + \
          ' ORDER BY m.date'
    c.execute(sql, (season,))
    return c.fetchall()


def matches_for_seasons(conn, start_season, end_season):
    c = conn.cursor()
    sql = 'SELECT DISTINCT ' + MATCH_COLS + \
          ' FROM ' + MATCH_TABLES + \
          ' WHERE ' + MATCH_TABLE_LINKS + \
          ' and m.season >= ? and m.season <= ? ' \
          ' ORDER BY m.date'
    c.execute(sql, (start_season, end_season,))
    return c.fetchall()


def matches_to_date(conn, season, date):
    c = conn.cursor()
    sql = 'SELECT DISTINCT ' + MATCH_COLS + \
          ' FROM ' + MATCH_TABLES + \
          ' WHERE ' + MATCH_TABLE_LINKS + \
          ' and m.season = ? and m.date < ? ' + \
          ' ORDER BY m.date'
    c.execute(sql, (season, date,))
    return c.fetchall()


def teams_for_season(conn, season):
    c = conn.cursor()
    c.execute('''SELECT DISTINCT t.id, t.short_name
                 FROM team t, match m, matchteam mt
                 WHERE (m.home_team = mt.id or m.away_team = mt.id)
                        and mt.team = t.id and m.season=?''', (season,))
    return c.fetchall()


# Find out which season a given date belongs to.
def season_by_date(conn, date):
    c = conn.cursor()
    c.execute('''SELECT season FROM match WHERE date < ? ORDER BY date DESC LIMIT 1''', (date,))
    return c.fetchone()['season']


def seasons_in_db(conn):
    c = conn.cursor()
    c.execute('''SELECT DISTINCT season FROM match ORDER BY season''')
    return c.fetchall()


def main():
    parser = argparse.ArgumentParser(epilog='''Commands: 1 = teams for a season(db, season)
                                                         2 = matches for season (db, season)''')
    arg_helper.default_args(parser, True)
    args = parser.parse_args()

    conn = create_connection(args.database)

    if args.command == 1:
        print('%s' % teams_for_season(conn, args.season))
    elif args.command == 2:
        pprint.pprint(matches_for_season(conn, args.season))


if __name__ == '__main__':
    main()