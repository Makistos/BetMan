# coding=utf-8
import sys
import db_helpers as dbh
import argparse
import arg_helper
import tables
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pprint


def gd_for_x_games(matches, team, sample_len):
    team_matches = [x for x in matches if x['team'] == team]


def __update_gd_for_team(conn, season, team_id):
    gf = 0
    ga = 0
    gfh = 0 # Goals for home
    gah = 0 # Goals against home
    gfa = 0 # Goals for away
    gaa = 0 # Goals against away

    c = conn.cursor()

    c.execute('SELECT mt.*, m.date '
              'FROM matchteam mt, match m '
              'WHERE mt.team = ? and (m.home_team = mt.id or m.away_team = mt.id) and m.season = ? '
              'ORDER BY m.date', (team_id, season,))
    matches = c.fetchall()
    for match in matches:
        gf += match['GF']
        ga += match['GA']
        if match['venue'] == 'h':
            gfh += match['GF']
            gah += match['GA']
            c.execute('UPDATE matchteamvar SET gf = ?, ga = ?, gfv = ?, gav = ? '
                      'WHERE matchteam = ?', (gf, ga, gfh, gah, match['id'],))
        else:
            gfa += match['GF']
            gaa += match['GA']
            c.execute('UPDATE matchteamvar SET gf = ?, ga = ?, gfv = ?, gav = ? '
                      'WHERE matchteam = ?', (gf, ga, gfa, gaa, match['id'],))
        conn.commit()


def update_gd_for_team(db, season, team_id):
    conn = dbh.create_connection(db)
    _update_gd_for_team(conn, season, team_id)
    conn.commit()


def update_gd_for_teams(db, season):
    conn = dbh.create_connection(db)
    teams = dbh.teams_for_season(db, season)

    for team in teams:
        _update_gd_for_team(conn, season, team['id'])


def gd_stats(db, count, venue=None):
    retval = []
    for i in range(200):
        retval.append([0,0,0])
    conn = dbh.create_connection(db)
    seasons = dbh.seasons_in_db(conn)
    for season in seasons:
        print("%s\n" % (season['season']))
        matches = dbh.matches_for_season(conn, season['season'])
        for match in matches:
            if match['home_matchno'] >= count and match['away_matchno'] >= count:
                home_form = tables.form_team(conn, match['home_name'], match['date'], count, venue)
                away_form = tables.form_team(conn, match['away_name'], match['date'], count, venue)
                home_gd = home_form['GF'] - home_form['GA']
                away_gd = away_form['GF'] - away_form['GA']
                result = match['home_goals'] - match['away_goals']
                if result > 0:
                    retval[100 + home_gd - away_gd][0] += 1
                elif result == 0:
                    retval[100 + home_gd - away_gd][1] += 1
                else:
                    retval[100 + home_gd - away_gd][2] += 1
    return retval


def plot_gd_bars(data):
    #Calculate starting and ending points
    for start in range(200):
        if sum(data[start]) > 0:
            break
    for end in range(200, -1, -1):
        if sum(data[end-1]) > 0:
            break
    N = end - start
    home_wins = tuple((x[0] for x in data[start:end]))
    draws = tuple((x[1] for x in data[start:end]))
    away_wins = tuple((x[2] for x in data[start:end]))
    ind = np.arange(N)
    print(home_wins)
    print(ind)
    p1 = plt.bar(ind, home_wins)
    p2 = plt.bar(ind, draws, bottom=home_wins)
    p3 = plt.bar(ind, away_wins, bottom=[i+j for i,j in zip(home_wins, draws)])
    plt.ylabel('Total')
    plt.xlabel('Goal difference')
    plt.xticks(ind, xrange(start-100, end-100))
    plt.legend((p1[0], p2[0], p3[0]), ('Home wins', 'Draws', 'Away wins'))
    plt.show()

def main():
    parser = argparse.ArgumentParser(epilog=
                                     '''
                                     Commands: 1 = update goal diff (db, season [, team]),
                                     2 = update goal difference stats (db, [, count] [, location] [, outfile)
                                     ''')
    arg_helper.default_args(parser, True)
    parser.add_argument('-n', '--count', help='Sample size for GD calculations', type=int, default=6)
    parser.add_argument('-l', '--location', help='Venue (home/away)')
    args = parser.parse_args()

    if args.command == 1:
        if args.team:
            update_gd_for_team(args.database, args.season, args.team)
        else:
            update_gd_for_teams(args.database, args.season)
    elif args.command == 2:
        result = gd_stats(args.database, args.count, args.location)
        if args.graphical:
            plot_gd_bars(result)
        for i in range(200):
            if sum(result[i]) > 0:
                print("%d: %d %d %d" % (i-100, result[i][0], result[i][1],  result[i][2]))
        print("Matches: %d" % sum(map(sum, result)))


if __name__ == '__main__':
    main()
