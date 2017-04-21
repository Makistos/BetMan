CREATE TABLE league
(
  id INTEGER PRIMARY KEY,
  long_name VARCHAR NULL,  -- E.g. English Premier League
  short_name VARCHAR NOT NULL UNIQUE, -- E.g. EPL
  csv_name VARCHAR NULL -- Name used in the CSV file, e.g. E0
);

CREATE TABLE team
(
  id INTEGER PRIMARY KEY,
  long_name VARCHAR NULL, -- E.g. Everton FC
  short_name VARCHAR NOT NULL UNIQUE, -- E.g. Everton
  abbreviation VARCHAR NULL, -- E.g. EFC
  league INTEGER NOT NULL,
  FOREIGN KEY(league) REFERENCES league(short_name)
);

CREATE TABLE match
(
  -- Match information.
  id INTEGER PRIMARY KEY,
  date DATETIME NOT NULL,
  season INTEGER NOT NULL, -- Season, year the season was played or started.
  home_team INTEGER NOT NULL,
  away_team INTEGER NOT NULL,
  FOREIGN KEY (home_team) REFERENCES matchteam(id),
  FOREIGN KEY (away_team) REFERENCES matchteam(id)
);

CREATE TABLE matchteam
(
  -- Match data for one team.
  id INTEGER PRIMARY KEY,
  team INTEGER NOT NULL,
  GF INTEGER, -- Goals scored by this team
  GA INTEGER, -- Goals against by this team
  venue CHAR, -- 'h' for home, 'a' for away
  matchno INTEGER, -- Match number for this team
  matchnov INTEGER, -- Match number per venue (home/away)
  FOREIGN KEY (team) REFERENCES team(short_name)
);

CREATE TABLE matchteamvar
(
  -- Variables calculated after each match for one one team.
  id INTEGER PRIMARY KEY,
  matchteam INTEGER NOT NULL,
  elo INTEGER,
  GF INTEGER, -- Goals for
  GA INTEGER, -- Goals against
  GFv INTEGER, -- Goals for per venue (home/away)
  GAv INTEGER, -- Goals against per venue (home/away)
  FOREIGN KEY(matchteam) REFERENCES matchteam(id)
);