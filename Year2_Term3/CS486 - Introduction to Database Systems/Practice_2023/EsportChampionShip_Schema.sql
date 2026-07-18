/* =========================================================
   EsportChampionship — Practice Database
   Dialect: T-SQL (SQL Server)
   Run this whole script to create and seed the database.
   ========================================================= */

CREATE DATABASE EsportChampionship;
GO
USE EsportChampionship;
GO

-- ---------------------------------------------------------
-- 1. Team
-- ---------------------------------------------------------
CREATE TABLE Team (
    TeamID   INT IDENTITY(1,1) PRIMARY KEY,
    TeamName VARCHAR(50) NOT NULL UNIQUE
);

-- ---------------------------------------------------------
-- 2. Player
-- ---------------------------------------------------------
CREATE TABLE Player (
    PlayerID INT IDENTITY(1,1) PRIMARY KEY,
    Nickname VARCHAR(50) NOT NULL UNIQUE,
    TeamID   INT NOT NULL,
    FOREIGN KEY (TeamID) REFERENCES Team(TeamID)
);

-- ---------------------------------------------------------
-- 3. Match
-- ---------------------------------------------------------
CREATE TABLE Match (
    MatchID    INT IDENTITY(1,1) PRIMARY KEY,
    Date       DATE NOT NULL,
    Team1ID    INT NOT NULL,
    Team2ID    INT NOT NULL,
    ScoreTeam1 INT NOT NULL,
    ScoreTeam2 INT NOT NULL,
    FOREIGN KEY (Team1ID) REFERENCES Team(TeamID),
    FOREIGN KEY (Team2ID) REFERENCES Team(TeamID),
    CHECK (Team1ID <> Team2ID)
);

-- ---------------------------------------------------------
-- 4. MatchPlayer  (intentionally contains a couple of "dirty"
--    Role values so Question 1 has something to clean up)
-- ---------------------------------------------------------
CREATE TABLE MatchPlayer (
    MatchID  INT NOT NULL,
    PlayerID INT NOT NULL,
    Role     VARCHAR(20) NOT NULL,
    Kills    INT NOT NULL DEFAULT 0,
    Deaths   INT NOT NULL DEFAULT 0,
    Assists  INT NOT NULL DEFAULT 0,
    PRIMARY KEY (MatchID, PlayerID),
    FOREIGN KEY (MatchID)  REFERENCES Match(MatchID),
    FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID)
);
GO

/* =========================================================
   SEED DATA
   ========================================================= */

INSERT INTO Team (TeamName) VALUES
('Vikings'), ('Dragons'), ('Phoenix'), ('Titans'), ('Wolves');

INSERT INTO Player (Nickname, TeamID) VALUES
('Ragnar', 1), ('Freya', 1), ('Bjorn', 1), ('Astrid', 1), ('Erik', 1),
('Draco', 2), ('Ember', 2), ('Ash', 2), ('Cinder', 2), ('Blaze', 2),
('Nyx', 3), ('Sol', 3), ('Luna', 3), ('Orion', 3), ('Vega', 3),
('Ajax', 4), ('Cronus', 4), ('Rhea', 4), ('Atlas', 4), ('Gaia', 4),
('Shadow', 5), ('Fang', 5), ('Luna2', 5), ('Howler', 5), ('Storm', 5);

INSERT INTO Match (Date, Team1ID, Team2ID, ScoreTeam1, ScoreTeam2) VALUES
('2025-05-24', 1, 2, 2, 1),   -- Vikings vs Dragons
('2025-05-24', 3, 4, 1, 2),   -- Phoenix vs Titans
('2025-05-25', 1, 3, 0, 2),   -- Vikings vs Phoenix
('2025-05-25', 2, 5, 2, 0),   -- Dragons vs Wolves
('2025-05-26', 4, 5, 1, 1),   -- Titans vs Wolves (draw handled loosely for practice)
('2025-05-26', 1, 4, 2, 0);   -- Vikings vs Titans

-- MatchPlayer for Match 1: Vikings(1) vs Dragons(2)
INSERT INTO MatchPlayer (MatchID, PlayerID, Role, Kills, Deaths, Assists) VALUES
(1, 1, 'Carry',        8, 2, 4),
(1, 2, 'Support',      1, 3, 12),
(1, 3, 'Mid',          6, 4, 5),
(1, 4, 'Offlane',      3, 5, 6),
(1, 5, 'Hard Support', 0, 4, 15),
(1, 6, 'Carry',        5, 6, 3),
(1, 7, 'jungler',      4, 5, 4),   -- dirty value: not in allowed list
(1, 8, 'Mid',          7, 3, 2),
(1, 9, 'Offlane',      2, 6, 3),
(1,10, 'Support',      0, 5, 9);

-- MatchPlayer for Match 2: Phoenix(3) vs Titans(4)
INSERT INTO MatchPlayer (MatchID, PlayerID, Role, Kills, Deaths, Assists) VALUES
(2,11, 'Carry',        10, 1, 3),
(2,12, 'Mid',           5, 3, 6),
(2,13, 'Support',       1, 2, 14),
(2,14, 'Offlane',       4, 4, 5),
(2,15, 'Hard Support',  0, 3, 11),
(2,16, 'Carry',         6, 4, 4),
(2,17, 'Mid',           7, 3, 3),
(2,18, 'roamer',        2, 5, 5),  -- dirty value: not in allowed list
(2,19, 'Offlane',       3, 4, 2),
(2,20, 'Support',       0, 4, 10);

-- MatchPlayer for Match 3: Vikings(1) vs Phoenix(3)
INSERT INTO MatchPlayer (MatchID, PlayerID, Role, Kills, Deaths, Assists) VALUES
(3, 1, 'Carry',        4, 5, 2),
(3, 2, 'Support',      0, 4, 8),
(3, 3, 'Mid',          3, 4, 3),
(3, 4, 'Offlane',      1, 5, 2),
(3, 5, 'Hard Support', 0, 5, 9),
(3,11, 'Carry',        9, 2, 5),
(3,12, 'Mid',          6, 3, 4),
(3,13, 'Support',      1, 2, 13),
(3,14, 'Offlane',      3, 3, 3),
(3,15, 'Hard Support', 0, 2, 10);

-- MatchPlayer for Match 4: Dragons(2) vs Wolves(5)
INSERT INTO MatchPlayer (MatchID, PlayerID, Role, Kills, Deaths, Assists) VALUES
(4, 6, 'Carry',        7, 2, 4),
(4, 7, 'Mid',          5, 3, 3),
(4, 8, 'Support',      1, 2, 11),
(4, 9, 'Offlane',      2, 4, 4),
(4,10, 'Hard Support', 0, 3, 12),
(4,21, 'Carry',        2, 6, 1),
(4,22, 'Mid',          3, 5, 2),
(4,23, 'Support',      0, 6, 6),
(4,24, 'Offlane',      1, 6, 2),
(4,25, 'Hard Support', 0, 5, 5);

-- MatchPlayer for Match 5: Titans(4) vs Wolves(5)
INSERT INTO MatchPlayer (MatchID, PlayerID, Role, Kills, Deaths, Assists) VALUES
(5,16, 'Carry',        6, 3, 3),
(5,17, 'Mid',          4, 3, 4),
(5,18, 'Support',      1, 3, 9),
(5,19, 'Offlane',      2, 4, 3),
(5,20, 'Hard Support', 0, 3, 10),
(5,21, 'Carry',        5, 4, 3),
(5,22, 'Mid',          4, 4, 4),
(5,23, 'Support',      0, 4, 8),
(5,24, 'Offlane',      2, 5, 2),
(5,25, 'Hard Support', 0, 4, 9);

-- MatchPlayer for Match 6: Vikings(1) vs Titans(4)
INSERT INTO MatchPlayer (MatchID, PlayerID, Role, Kills, Deaths, Assists) VALUES
(6, 1, 'Carry',        9, 1, 5),
(6, 2, 'Support',      0, 2, 13),
(6, 3, 'Mid',          6, 2, 4),
(6, 4, 'Offlane',      3, 3, 3),
(6, 5, 'Hard Support', 1, 2, 12),
(6,16, 'Carry',        3, 5, 2),
(6,17, 'Mid',          2, 5, 3),
(6,18, 'Support',      0, 6, 5),
(6,19, 'Offlane',      1, 5, 2),
(6,20, 'Hard Support', 0, 5, 6);
GO
