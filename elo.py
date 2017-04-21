import plot

from footballdatacouk import db

we = lambda old, opp, adj:  (1.0 / (10**(-(old - opp + adj)/400.0) + 1.0))
team_matches = lambda li, team: [x for x in li if x[db.HOME_TEAM] == team or x[db.AWAY_TEAM] == team]

TXT_FIELDS = [db.DATE, db.FTR, db.HOME_TEAM, db.FTHG, db.FTAG, db.AWAY_TEAM, db.HE, db.AE, db.HEC, db.AEC]
TXT_FIELDS2 = [db.DATE, db.FTR, db.HOME_TEAM, db.FTHG, db.FTAG, db.AWAY_TEAM, db.HE, db.AE, db.HEC, db.AEC]


def prev_elo_value(li, team):
    e = 1000
    c = 0
    if len(li) == 0:
        return 1000, 0
    if li[-1][db.HOME_TEAM] == team:
        if db.HE in li[-1]:
            e = li[-1][db.HE]
        if db.HEC in li[-1]:
            c = li[-1][db.HEC]
    elif li[-1][db.AWAY_TEAM] == team:
        if db.AE in li[-1]:
            e = li[-1][db.AE]
        if db.AEC in li[-1]:
            c = li[-1][db.AEC]

    return e, c

extract_dict = lambda keys, dict: reduce(lambda x, y: x.update({y[0]: y[1]}) or x,
                                         map(None, keys, map(dict.get, keys)), {})


def elo_calculate(matches):
    for i in range(len(matches)):
        match = list(matches)[i]
        ht_matches = team_matches(matches[0:i-1], match[db.HOME_TEAM])
        at_matches = team_matches(matches[0:i-1], match[db.AWAY_TEAM])
        (old_home_elo, old_home_change) = prev_elo_value(ht_matches, match[db.HOME_TEAM])
        (old_away_elo, old_away_change) = prev_elo_value(at_matches, match[db.AWAY_TEAM])
        match[db.HE] = old_home_elo + old_home_change
        match[db.AE] = old_away_elo + old_away_change

        (match[db.HEC], match[db.AEC]) = elo_adjust(match, match[db.HE], match[db.AE])
        if match[db.HOME_TEAM] == 'Everton' or match[db.AWAY_TEAM] == 'Everton':
            print extract_dict(TXT_FIELDS, match)


def elo_adjust(match, home_elo, away_elo):

    home = elo_calc_change(int(home_elo), int(away_elo), True, int(match[db.FTHG]), int(match[db.FTAG]))
    away = elo_calc_change(int(away_elo), int(home_elo), False, int(match[db.FTAG]), int(match[db.FTHG]))

    return home, away


def elo_calc_change(old_value, opp_value, is_home, scored, conceded):
    """
    @rtype : float
    @param old_value: Current value that will be fixed
    @param opp_value: Opponent's rating
    @param is_home: Was this a home game?
    @param scored: How many goals team scored
    @param conceded: How many goals team conceded
    @return Change in rating
    This function calculates the change in the rating using the world football
    ELO rating. The formula is:
    R = KG * (W - We)
    Where G is goal difference. If the game was won with one goal or less this is not adjusted.
    For two goal difference it is 3/2 and if it's greater than two, (11+N)/8 where N is goal difference.
    K is 20 which is the same as the coefficient in friendly international matches. Adjusting this will make
    changes bigger or smaller.
    W is the result, win = 1, draw = 0,5, loss = 0.
    We is expected result, calculated with
    We = 1 / (10^(-dr/400)+1)
    Where dr is the difference in rating. 100 is added if this was a home match.
    """

    g_diff = abs(scored - conceded)

    g = 0.0

    if g_diff < 2:
        g = 1.0
    elif g_diff == 2:
        g = 3/2.0
    else:
        g = (11 + g_diff) / 8.0

    home_adj = 0.0
    if is_home:
        home_adj = 100.0
    else:
        home_adj = -100.0

    if scored > conceded:
        result = 1.0
    elif scored == conceded:
        result = 0.5
    else:
        result = 0.0

    r = 40.0 * g * (result - we(old_value, opp_value, home_adj))

    return r


def elo_plot(matches):
    li2 = [int(m[db.FTHG]) - int(m[db.FTAG]) for m in matches]
    li1 = [we(m[db.HE], m[db.AE], 100) for m in matches]
    plot.plot_test(li1, li2)