/*
    Sports Training Database - SQL Server generation script

    Creates:
      6 clubs
      18 coaches
      24 training programs
      48 training sessions
      96 coaching assignments
      60 athletes
      18 prerequisite relationships
      500+ performance records

    WARNING: Rerunning this script deletes and recreates the tables inside
    SportsTrainingDB. It does not delete the database itself.
*/

USE master;
GO

IF DB_ID('SportsTrainingDB') IS NULL
    CREATE DATABASE SportsTrainingDB;
GO

ALTER DATABASE SportsTrainingDB SET ALLOW_SNAPSHOT_ISOLATION ON;
GO

USE SportsTrainingDB;
GO

/* ================================================================
   1. REMOVE THE OLD TABLES SO THE SCRIPT CAN BE RERUN
   ================================================================ */

IF OBJECT_ID('dbo.CLUB', 'U') IS NOT NULL
   AND EXISTS (
       SELECT 1
       FROM sys.foreign_keys
       WHERE name = 'FK_CLUB_HEAD_COACH'
   )
BEGIN
    ALTER TABLE dbo.CLUB DROP CONSTRAINT FK_CLUB_HEAD_COACH;
END;
GO

DROP TABLE IF EXISTS dbo.PROGRAM_PREREQUISITE;
DROP TABLE IF EXISTS dbo.PERFORMANCE;
DROP TABLE IF EXISTS dbo.COACHING;
DROP TABLE IF EXISTS dbo.TRAINING_SESSION;
DROP TABLE IF EXISTS dbo.ATHLETE;
DROP TABLE IF EXISTS dbo.TRAINING_PROGRAM;
DROP TABLE IF EXISTS dbo.COACH;
DROP TABLE IF EXISTS dbo.CLUB;
GO

/* ================================================================
   2. CREATE TABLES
   ================================================================ */

CREATE TABLE dbo.CLUB
(
    club_id       VARCHAR(10)   NOT NULL,
    club_name     NVARCHAR(100) NOT NULL,
    stadium       NVARCHAR(100) NOT NULL,
    head_coach_id VARCHAR(10)   NULL,

    CONSTRAINT PK_CLUB PRIMARY KEY (club_id)
);
GO

CREATE TABLE dbo.COACH
(
    coach_id   VARCHAR(10)   NOT NULL,
    coach_name NVARCHAR(100) NOT NULL,
    phone      VARCHAR(20)   NULL,
    club_id    VARCHAR(10)   NOT NULL,
    salary     INT           NOT NULL,

    CONSTRAINT PK_COACH PRIMARY KEY (coach_id),
    CONSTRAINT FK_COACH_CLUB FOREIGN KEY (club_id)
        REFERENCES dbo.CLUB(club_id),
    CONSTRAINT CK_COACH_SALARY CHECK (salary > 0)
);
GO

ALTER TABLE dbo.CLUB
ADD CONSTRAINT FK_CLUB_HEAD_COACH
    FOREIGN KEY (head_coach_id) REFERENCES dbo.COACH(coach_id);
GO

CREATE TABLE dbo.ATHLETE
(
    athlete_id   VARCHAR(10)   NOT NULL,
    athlete_name NVARCHAR(100) NOT NULL,
    gender       CHAR(1)       NOT NULL,
    birthdate    DATE          NOT NULL,
    team_level   VARCHAR(20)   NOT NULL,
    club_id      VARCHAR(10)   NOT NULL,

    CONSTRAINT PK_ATHLETE PRIMARY KEY (athlete_id),
    CONSTRAINT FK_ATHLETE_CLUB FOREIGN KEY (club_id)
        REFERENCES dbo.CLUB(club_id),
    CONSTRAINT CK_ATHLETE_GENDER CHECK (gender IN ('M', 'F'))
);
GO

CREATE TABLE dbo.TRAINING_PROGRAM
(
    program_id   VARCHAR(10)   NOT NULL,
    program_name NVARCHAR(100) NOT NULL,
    focus_area   NVARCHAR(100) NOT NULL,
    club_id      VARCHAR(10)   NOT NULL,

    CONSTRAINT PK_TRAINING_PROGRAM PRIMARY KEY (program_id),
    CONSTRAINT FK_PROGRAM_CLUB FOREIGN KEY (club_id)
        REFERENCES dbo.CLUB(club_id)
);
GO

CREATE TABLE dbo.TRAINING_SESSION
(
    session_id    INT         NOT NULL,
    program_id    VARCHAR(10) NOT NULL,
    season        VARCHAR(20) NOT NULL,
    training_year INT         NOT NULL,
    capacity      INT         NOT NULL,

    CONSTRAINT PK_TRAINING_SESSION PRIMARY KEY (session_id),
    CONSTRAINT FK_SESSION_PROGRAM FOREIGN KEY (program_id)
        REFERENCES dbo.TRAINING_PROGRAM(program_id),
    CONSTRAINT CK_SESSION_CAPACITY CHECK (capacity > 0)
);
GO

CREATE TABLE dbo.COACHING
(
    session_id   INT         NOT NULL,
    coach_id     VARCHAR(10) NOT NULL,
    coaching_role VARCHAR(30) NOT NULL,

    CONSTRAINT PK_COACHING PRIMARY KEY (session_id, coach_id),
    CONSTRAINT FK_COACHING_SESSION FOREIGN KEY (session_id)
        REFERENCES dbo.TRAINING_SESSION(session_id),
    CONSTRAINT FK_COACHING_COACH FOREIGN KEY (coach_id)
        REFERENCES dbo.COACH(coach_id)
);
GO

CREATE TABLE dbo.PERFORMANCE
(
    session_id INT         NOT NULL,
    athlete_id VARCHAR(10) NOT NULL,
    score_100  INT         NULL,
    rating     CHAR(1)     NULL,

    CONSTRAINT PK_PERFORMANCE PRIMARY KEY (session_id, athlete_id),
    CONSTRAINT FK_PERFORMANCE_SESSION FOREIGN KEY (session_id)
        REFERENCES dbo.TRAINING_SESSION(session_id),
    CONSTRAINT FK_PERFORMANCE_ATHLETE FOREIGN KEY (athlete_id)
        REFERENCES dbo.ATHLETE(athlete_id),
    -- No upper limit is enforced because Question 11 intentionally
    -- multiplies an existing score by 1.1.
    CONSTRAINT CK_PERFORMANCE_SCORE CHECK
        (score_100 IS NULL OR score_100 >= 0),
    CONSTRAINT CK_PERFORMANCE_RATING CHECK
        (rating IS NULL OR rating IN ('A', 'B', 'C', 'D', 'F'))
);
GO

CREATE TABLE dbo.PROGRAM_PREREQUISITE
(
    program_id     VARCHAR(10) NOT NULL,
    prerequisite_id VARCHAR(10) NOT NULL,

    CONSTRAINT PK_PROGRAM_PREREQUISITE
        PRIMARY KEY (program_id, prerequisite_id),
    CONSTRAINT FK_PREREQUISITE_PROGRAM FOREIGN KEY (program_id)
        REFERENCES dbo.TRAINING_PROGRAM(program_id),
    CONSTRAINT FK_PREREQUISITE_REQUIRED FOREIGN KEY (prerequisite_id)
        REFERENCES dbo.TRAINING_PROGRAM(program_id),
    CONSTRAINT CK_PREREQUISITE_DIFFERENT
        CHECK (program_id <> prerequisite_id)
);
GO

/* ================================================================
   3. INSERT CLUBS AND COACHES
   ================================================================ */

INSERT INTO dbo.CLUB (club_id, club_name, stadium, head_coach_id)
VALUES
    ('CL01', N'Falcon Athletics Club', N'Falcon Arena', NULL),
    ('CL02', N'Blue Wave Aquatics',    N'Wave Center',  NULL),
    ('CL03', N'Iron Peak Fitness',     N'Peak Stadium', NULL),
    ('CL04', N'Golden Racket Club',    N'Golden Court', NULL),
    ('CL05', N'Thunder Football Club', N'Thunder Field',NULL),
    ('CL06', N'Phoenix Endurance Club',N'Phoenix Park', NULL);
GO

;WITH ClubNumbers AS
(
    SELECT number AS club_no
    FROM (VALUES (1), (2), (3), (4), (5), (6)) C(number)
),
CoachNumbers AS
(
    SELECT number AS coach_no
    FROM (VALUES (1), (2), (3)) C(number)
)
INSERT INTO dbo.COACH (coach_id, coach_name, phone, club_id, salary)
SELECT
    'CO' + CAST(club_no AS VARCHAR(1))
         + RIGHT('0' + CAST(coach_no AS VARCHAR(2)), 2),
    N'Coach ' + CAST(club_no AS NVARCHAR(2))
              + N'-' + CAST(coach_no AS NVARCHAR(2)),
    '090' + CAST(club_no AS VARCHAR(1))
          + '0000' + CAST(coach_no AS VARCHAR(1)),
    'CL' + RIGHT('0' + CAST(club_no AS VARCHAR(2)), 2),
    40000 + club_no * 6000 + coach_no * 2500
FROM ClubNumbers
CROSS JOIN CoachNumbers;
GO

UPDATE dbo.CLUB
SET head_coach_id =
    'CO' + RIGHT(club_id, 1) + '01';
GO

/* ================================================================
   4. INSERT 60 ATHLETES
   ================================================================ */

;WITH Numbers AS
(
    SELECT TOP (60)
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
    FROM sys.all_objects
)
INSERT INTO dbo.ATHLETE
    (athlete_id, athlete_name, gender, birthdate, team_level, club_id)
SELECT
    'A' + RIGHT('000' + CAST(n AS VARCHAR(3)), 3),
    N'Athlete ' + RIGHT('000' + CAST(n AS NVARCHAR(3)), 3),
    CASE WHEN n % 2 = 0 THEN 'F' ELSE 'M' END,
    DATEADD(DAY, -(n * 95), CAST('2005-12-31' AS DATE)),
    CASE n % 3
        WHEN 0 THEN 'Elite'
        WHEN 1 THEN 'Intermediate'
        ELSE 'Beginner'
    END,
    'CL' + RIGHT('0' + CAST(((n - 1) % 6) + 1 AS VARCHAR(2)), 2)
FROM Numbers;
GO

/* ================================================================
   5. INSERT 24 PROGRAMS: FOUR PER CLUB

   Program 1 = foundation
   Program 2 = intermediate; requires Program 1
   Program 3 = advanced; requires Program 2
   Program 4 = recovery; requires Program 1
   ================================================================ */

;WITH ClubNumbers AS
(
    SELECT number AS club_no
    FROM (VALUES (1), (2), (3), (4), (5), (6)) C(number)
),
ProgramNumbers AS
(
    SELECT number AS program_no
    FROM (VALUES (1), (2), (3), (4)) P(number)
)
INSERT INTO dbo.TRAINING_PROGRAM
    (program_id, program_name, focus_area, club_id)
SELECT
    'P' + CAST(club_no AS VARCHAR(1))
        + RIGHT('0' + CAST(program_no AS VARCHAR(2)), 2),
    CHOOSE(program_no,
        N'Foundation Skills',
        N'Intermediate Development',
        N'Advanced Performance',
        N'Recovery and Conditioning'),
    CHOOSE(club_no,
        N'Athletics',
        N'Aquatics',
        N'Strength',
        N'Racket Sports',
        N'Football',
        N'Endurance'),
    'CL' + RIGHT('0' + CAST(club_no AS VARCHAR(2)), 2)
FROM ClubNumbers
CROSS JOIN ProgramNumbers;
GO

/* ================================================================
   6. INSERT PREREQUISITE RELATIONSHIPS
   ================================================================ */

;WITH ClubNumbers AS
(
    SELECT number AS club_no
    FROM (VALUES (1), (2), (3), (4), (5), (6)) C(number)
)
INSERT INTO dbo.PROGRAM_PREREQUISITE (program_id, prerequisite_id)
SELECT 'P' + CAST(club_no AS VARCHAR(1)) + '02',
       'P' + CAST(club_no AS VARCHAR(1)) + '01'
FROM ClubNumbers
UNION ALL
SELECT 'P' + CAST(club_no AS VARCHAR(1)) + '03',
       'P' + CAST(club_no AS VARCHAR(1)) + '02'
FROM ClubNumbers
UNION ALL
SELECT 'P' + CAST(club_no AS VARCHAR(1)) + '04',
       'P' + CAST(club_no AS VARCHAR(1)) + '01'
FROM ClubNumbers;
GO

/* ================================================================
   7. INSERT 48 SESSIONS: TWO PER PROGRAM

   Session ID format:
     club number, program number, occurrence number
     Example: 132 = Club 1, Program 3, second session
   ================================================================ */

;WITH ClubNumbers AS
(
    SELECT number AS club_no
    FROM (VALUES (1), (2), (3), (4), (5), (6)) C(number)
),
ProgramNumbers AS
(
    SELECT number AS program_no
    FROM (VALUES (1), (2), (3), (4)) P(number)
),
Occurrences AS
(
    SELECT number AS occurrence_no
    FROM (VALUES (1), (2)) O(number)
)
INSERT INTO dbo.TRAINING_SESSION
    (session_id, program_id, season, training_year, capacity)
SELECT
    club_no * 100 + program_no * 10 + occurrence_no,
    'P' + CAST(club_no AS VARCHAR(1))
        + RIGHT('0' + CAST(program_no AS VARCHAR(2)), 2),
    CASE occurrence_no WHEN 1 THEN 'Spring' ELSE 'Autumn' END,
    2026,
    20 + club_no * 2 + program_no
FROM ClubNumbers
CROSS JOIN ProgramNumbers
CROSS JOIN Occurrences;
GO

/* ================================================================
   8. INSERT 96 COACHING ASSIGNMENTS: TWO PER SESSION
   ================================================================ */

INSERT INTO dbo.COACHING (session_id, coach_id, coaching_role)
SELECT
    S.session_id,
    'CO' + SUBSTRING(S.program_id, 2, 1)
         + RIGHT('0' + CAST(((CAST(RIGHT(S.program_id, 1) AS INT) - 1) % 3) + 1
           AS VARCHAR(2)), 2),
    'Lead Coach'
FROM dbo.TRAINING_SESSION S;

INSERT INTO dbo.COACHING (session_id, coach_id, coaching_role)
SELECT
    S.session_id,
    'CO' + SUBSTRING(S.program_id, 2, 1)
         + RIGHT('0' + CAST((CAST(RIGHT(S.program_id, 1) AS INT) % 3) + 1
           AS VARCHAR(2)), 2),
    'Assistant Coach'
FROM dbo.TRAINING_SESSION S;
GO

/* ================================================================
   9. INSERT CONTROLLED PERFORMANCE ROWS

   These rows create predictable cases for testing:
     A001 has passed at least one program from every club.
     A002 has only passed programs from some clubs.
     A003 is enrolled in an advanced program without passing its
          intermediate prerequisite.
     A004 is enrolled in a recovery program and has passed its prerequisite.
   ================================================================ */

INSERT INTO dbo.PERFORMANCE (session_id, athlete_id, score_100, rating)
VALUES
    (111, 'A001', 91, 'A'),
    (211, 'A001', 84, 'B'),
    (311, 'A001', 76, 'B'),
    (411, 'A001', 88, 'B'),
    (511, 'A001', 82, 'B'),
    (611, 'A001', 95, 'A'),
    (121, 'A001', 79, 'B'),
    (131, 'A001', NULL, NULL),

    (111, 'A002', 73, 'B'),
    (211, 'A002', 67, 'C'),
    (311, 'A002', 44, 'F'),
    (321, 'A002', NULL, NULL),

    (111, 'A003', 75, 'B'),
    (121, 'A003', 45, 'F'),
    (131, 'A003', NULL, NULL),

    (211, 'A004', 86, 'B'),
    (241, 'A004', NULL, NULL),

    (411, 'A005', 62, 'C'),
    (421, 'A005', 58, 'C'),
    (431, 'A005', 49, 'F'),
    (441, 'A005', NULL, NULL);
GO

/* ================================================================
   10. GENERATE 500+ ADDITIONAL PERFORMANCE ROWS

   The formula is deterministic: rerunning the script produces the
   same data. Some scores are NULL to represent current enrollment.
   ================================================================ */

;WITH AthleteNumbers AS
(
    SELECT TOP (55)
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) + 5 AS n
    FROM sys.all_objects
)
INSERT INTO dbo.PERFORMANCE (session_id, athlete_id, score_100, rating)
SELECT
    S.session_id,
    'A' + RIGHT('000' + CAST(A.n AS VARCHAR(3)), 3),
    X.calculated_score,
    CASE
        WHEN X.calculated_score IS NULL THEN NULL
        WHEN X.calculated_score >= 90 THEN 'A'
        WHEN X.calculated_score >= 75 THEN 'B'
        WHEN X.calculated_score >= 60 THEN 'C'
        WHEN X.calculated_score >= 50 THEN 'D'
        ELSE 'F'
    END
FROM AthleteNumbers A
CROSS JOIN dbo.TRAINING_SESSION S
CROSS APPLY
(
    SELECT CASE
        WHEN (A.n + S.session_id) % 13 = 0 THEN NULL
        ELSE 35 + ((A.n * 7 + S.session_id * 3) % 66)
    END AS calculated_score
) X
WHERE (A.n + S.session_id) % 5 = 0;
GO

/* ================================================================
   11. USEFUL INDEXES

   There is deliberately no UNIQUE constraint on
   (club_id, program_name), because Question 7 asks you to enforce
   that rule using a trigger.
   ================================================================ */

CREATE INDEX IX_COACH_CLUB
    ON dbo.COACH(club_id);

CREATE INDEX IX_ATHLETE_CLUB
    ON dbo.ATHLETE(club_id);

CREATE INDEX IX_PROGRAM_CLUB
    ON dbo.TRAINING_PROGRAM(club_id);

CREATE INDEX IX_SESSION_PROGRAM
    ON dbo.TRAINING_SESSION(program_id);

CREATE INDEX IX_PERFORMANCE_ATHLETE
    ON dbo.PERFORMANCE(athlete_id);
GO

/* ================================================================
   12. VERIFY THE GENERATED DATA
   ================================================================ */

SELECT 'CLUB' AS table_name, COUNT(*) AS row_count FROM dbo.CLUB
UNION ALL
SELECT 'COACH', COUNT(*) FROM dbo.COACH
UNION ALL
SELECT 'ATHLETE', COUNT(*) FROM dbo.ATHLETE
UNION ALL
SELECT 'TRAINING_PROGRAM', COUNT(*) FROM dbo.TRAINING_PROGRAM
UNION ALL
SELECT 'TRAINING_SESSION', COUNT(*) FROM dbo.TRAINING_SESSION
UNION ALL
SELECT 'COACHING', COUNT(*) FROM dbo.COACHING
UNION ALL
SELECT 'PERFORMANCE', COUNT(*) FROM dbo.PERFORMANCE
UNION ALL
SELECT 'PROGRAM_PREREQUISITE', COUNT(*) FROM dbo.PROGRAM_PREREQUISITE;
GO

PRINT 'SportsTrainingDB was generated successfully.';
GO
