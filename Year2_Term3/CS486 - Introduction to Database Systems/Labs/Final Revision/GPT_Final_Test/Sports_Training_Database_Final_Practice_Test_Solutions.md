# Sports Training Database - Corrected Solutions

These solutions use Microsoft SQL Server syntax and the schema in `Generate_SportsTrainingDB.sql`.

Important interpretations:

- A program is passed when `score_100 >= 50`.
- A `PERFORMANCE` row represents enrollment.
- Questions 5 and 14 refer to direct prerequisites unless recursive prerequisites are explicitly requested.

## Question 1

Find the names of all training programs that have at least one prerequisite, but none of their prerequisite programs have prerequisites of their own.

```sql
SELECT
    program.program_id,
    program.program_name
FROM TRAINING_PROGRAM AS program
WHERE EXISTS (
    SELECT 1
    FROM PROGRAM_PREREQUISITE AS direct_prereq
    WHERE direct_prereq.program_id = program.program_id
)
AND NOT EXISTS (
    SELECT 1
    FROM PROGRAM_PREREQUISITE AS direct_prereq
    JOIN PROGRAM_PREREQUISITE AS prereq_of_prereq
      ON prereq_of_prereq.program_id = direct_prereq.prerequisite_id
    WHERE direct_prereq.program_id = program.program_id
);
```

The first `EXISTS` requires at least one prerequisite. The second test rejects a program if any direct prerequisite has a prerequisite of its own.

## Question 2

Identify all coaches who are coaching a training session in the same season and training year as the head coach of their own club.

```sql
SELECT DISTINCT
    coach.coach_id,
    coach.coach_name
FROM COACH AS coach
JOIN CLUB AS club
    ON club.club_id = coach.club_id
JOIN COACHING AS coach_assignment
    ON coach_assignment.coach_id = coach.coach_id
JOIN TRAINING_SESSION AS coach_session
    ON coach_session.session_id = coach_assignment.session_id
JOIN COACHING AS head_assignment
    ON head_assignment.coach_id = club.head_coach_id
JOIN TRAINING_SESSION AS head_session
    ON head_session.session_id = head_assignment.session_id
WHERE head_session.season = coach_session.season
  AND head_session.training_year = coach_session.training_year;
```

The aliases separate the ordinary coach's sessions from the head coach's sessions.

## Question 3

Find all athletes who have taken and passed at least one training program offered by every club in the database.

```sql
SELECT
    athlete.athlete_id,
    athlete.athlete_name
FROM ATHLETE AS athlete
JOIN PERFORMANCE AS performance
    ON performance.athlete_id = athlete.athlete_id
JOIN TRAINING_SESSION AS session
    ON session.session_id = performance.session_id
JOIN TRAINING_PROGRAM AS program
    ON program.program_id = session.program_id
WHERE performance.score_100 >= 50
GROUP BY
    athlete.athlete_id,
    athlete.athlete_name
HAVING COUNT(DISTINCT program.club_id) = (
    SELECT COUNT(*)
    FROM CLUB
);
```

This is relational division: clubs covered by the athlete must equal all clubs.

## Question 4

Find the club or clubs whose coaches have the highest average salary.

```sql
SELECT TOP (1) WITH TIES
    club.club_id,
    club.club_name,
    AVG(CAST(coach.salary AS DECIMAL(18, 2))) AS average_salary
FROM CLUB AS club
JOIN COACH AS coach
    ON coach.club_id = club.club_id
GROUP BY
    club.club_id,
    club.club_name
ORDER BY average_salary DESC;
```

`WITH TIES` retains clubs sharing the highest average. Casting prevents integer-average truncation.

## Question 5

Identify athletes who are currently enrolled in a training program but have not yet passed any of that program's prerequisites. A `NULL` score represents current enrollment.

```sql
SELECT DISTINCT
    athlete.athlete_id,
    athlete.athlete_name
FROM ATHLETE AS athlete
JOIN PERFORMANCE AS current_performance
    ON current_performance.athlete_id = athlete.athlete_id
JOIN TRAINING_SESSION AS current_session
    ON current_session.session_id = current_performance.session_id
WHERE current_performance.score_100 IS NULL
  AND EXISTS (
      SELECT 1
      FROM PROGRAM_PREREQUISITE AS prerequisite
      WHERE prerequisite.program_id = current_session.program_id
  )
  AND NOT EXISTS (
      SELECT 1
      FROM PROGRAM_PREREQUISITE AS prerequisite
      JOIN TRAINING_SESSION AS prerequisite_session
        ON prerequisite_session.program_id = prerequisite.prerequisite_id
      JOIN PERFORMANCE AS prerequisite_performance
        ON prerequisite_performance.session_id = prerequisite_session.session_id
       AND prerequisite_performance.athlete_id = athlete.athlete_id
      WHERE prerequisite.program_id = current_session.program_id
        AND prerequisite_performance.score_100 >= 50
  );
```

The program must actually have a prerequisite, and no passing record may exist for any direct prerequisite.

## Question 6

For each club, find the coach who has coached the greatest number of unique training programs. Include ties.

```sql
WITH ProgramCounts AS
(
    SELECT
        club.club_id,
        club.club_name,
        coach.coach_id,
        coach.coach_name,
        COUNT(DISTINCT session.program_id) AS program_count
    FROM CLUB AS club
    JOIN COACH AS coach
        ON coach.club_id = club.club_id
    LEFT JOIN COACHING AS coaching
        ON coaching.coach_id = coach.coach_id
    LEFT JOIN TRAINING_SESSION AS session
        ON session.session_id = coaching.session_id
    GROUP BY
        club.club_id,
        club.club_name,
        coach.coach_id,
        coach.coach_name
),
RankedCoaches AS
(
    SELECT *,
        RANK() OVER (
            PARTITION BY club_id
            ORDER BY program_count DESC
        ) AS coach_rank
    FROM ProgramCounts
)
SELECT
    club_id,
    club_name,
    coach_id,
    coach_name,
    program_count
FROM RankedCoaches
WHERE coach_rank = 1;
```

`RANK()` restarts for each club and assigns rank 1 to all tied leaders.

## Question 7

Identify the table of influence and write a trigger enforcing that no two programs in the same club have the same program name.

Table of influence: `TRAINING_PROGRAM` for `INSERT` and `UPDATE`.

```sql
CREATE OR ALTER TRIGGER dbo.same_program_name
ON dbo.TRAINING_PROGRAM
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 1
        FROM inserted AS inserted_program
        JOIN dbo.TRAINING_PROGRAM AS existing_program
          ON existing_program.club_id = inserted_program.club_id
         AND existing_program.program_name = inserted_program.program_name
         AND existing_program.program_id <> inserted_program.program_id
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 50001,
              'Two training programs in the same club cannot have the same name.',
              1;
    END;
END;
GO
```

The trigger is set-based, so it also handles multi-row inserts and updates.

## Question 8

Write a trigger that performs a cascading delete when a club is deleted without violating foreign-key constraints.

Affected tables: `CLUB`, `COACH`, `ATHLETE`, `TRAINING_PROGRAM`, `TRAINING_SESSION`, `COACHING`, `PERFORMANCE`, and `PROGRAM_PREREQUISITE`.

```sql
CREATE OR ALTER TRIGGER dbo.trg_DeleteClub
ON dbo.CLUB
INSTEAD OF DELETE
AS
BEGIN
    UPDATE club
    SET head_coach_id = NULL
    FROM dbo.CLUB AS club
    JOIN dbo.COACH AS coach
        ON coach.coach_id = club.head_coach_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = coach.club_id;

    DELETE performance
    FROM dbo.PERFORMANCE AS performance
    JOIN dbo.ATHLETE AS athlete
        ON athlete.athlete_id = performance.athlete_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = athlete.club_id;

    DELETE performance
    FROM dbo.PERFORMANCE AS performance
    JOIN dbo.TRAINING_SESSION AS session
        ON session.session_id = performance.session_id
    JOIN dbo.TRAINING_PROGRAM AS program
        ON program.program_id = session.program_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    DELETE coaching
    FROM dbo.COACHING AS coaching
    JOIN dbo.COACH AS coach
        ON coach.coach_id = coaching.coach_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = coach.club_id;

    DELETE coaching
    FROM dbo.COACHING AS coaching
    JOIN dbo.TRAINING_SESSION AS session
        ON session.session_id = coaching.session_id
    JOIN dbo.TRAINING_PROGRAM AS program
        ON program.program_id = session.program_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    DELETE prerequisite
    FROM dbo.PROGRAM_PREREQUISITE AS prerequisite
    JOIN dbo.TRAINING_PROGRAM AS program
        ON program.program_id = prerequisite.program_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    DELETE prerequisite
    FROM dbo.PROGRAM_PREREQUISITE AS prerequisite
    JOIN dbo.TRAINING_PROGRAM AS program
        ON program.program_id = prerequisite.prerequisite_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    DELETE session
    FROM dbo.TRAINING_SESSION AS session
    JOIN dbo.TRAINING_PROGRAM AS program
        ON program.program_id = session.program_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    DELETE athlete
    FROM dbo.ATHLETE AS athlete
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = athlete.club_id;

    DELETE coach
    FROM dbo.COACH AS coach
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = coach.club_id;

    DELETE program
    FROM dbo.TRAINING_PROGRAM AS program
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    DELETE club
    FROM dbo.CLUB AS club
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = club.club_id;
END;
GO
```

Dependent rows are deleted from the leaves of the relationship graph toward `CLUB`.

## Question 9

Create a procedure that reads a score, waits ten seconds, and reads it again.

```sql
CREATE OR ALTER PROCEDURE dbo.Read_Score_Twice
    @athlete_id VARCHAR(10),
    @session_id INT
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;

        SELECT score_100
        FROM dbo.PERFORMANCE
        WHERE athlete_id = @athlete_id
          AND session_id = @session_id;

        WAITFOR DELAY '00:00:10';

        SELECT score_100
        FROM dbo.PERFORMANCE
        WHERE athlete_id = @athlete_id
          AND session_id = @session_id;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
```

Both reads must be inside the same transaction for the isolation-level comparison in Question 12.

## Question 10

Create a procedure that deletes an athlete's performance. Roll back if the athlete or session does not exist; otherwise delete the matching record and commit.

```sql
CREATE OR ALTER PROCEDURE dbo.delete_performance
    @athlete_id VARCHAR(10),
    @session_id INT
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;

        IF NOT EXISTS (
            SELECT 1
            FROM dbo.ATHLETE
            WHERE athlete_id = @athlete_id
        )
        OR NOT EXISTS (
            SELECT 1
            FROM dbo.TRAINING_SESSION
            WHERE session_id = @session_id
        )
        BEGIN
            ROLLBACK TRANSACTION;
            RETURN;
        END;

        DELETE FROM dbo.PERFORMANCE
        WHERE athlete_id = @athlete_id
          AND session_id = @session_id;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
```

If both IDs exist but the matching performance does not, the delete affects zero rows and the transaction still commits.

## Question 11

Create a procedure that multiplies an athlete's score by `1.1`. Update and commit when both IDs exist; otherwise make no update and still commit.

```sql
CREATE OR ALTER PROCEDURE dbo.multiply_athlete_score
    @athlete_id VARCHAR(10),
    @session_id INT
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;

        IF EXISTS (
            SELECT 1
            FROM dbo.ATHLETE
            WHERE athlete_id = @athlete_id
        )
        AND EXISTS (
            SELECT 1
            FROM dbo.TRAINING_SESSION
            WHERE session_id = @session_id
        )
        BEGIN
            UPDATE dbo.PERFORMANCE
            SET score_100 = score_100 * 1.1
            WHERE athlete_id = @athlete_id
              AND session_id = @session_id;
        END;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
```

Because `score_100` is an integer column, a fractional result cannot be stored exactly.

## Question 12

Analyze Procedures 9-11 when they run concurrently under each SQL Server isolation level.

| Isolation level | Result |
|---|---|
| `READ UNCOMMITTED` | Procedure 9 may read uncommitted data, two different values, or a disappearing row. Dirty reads, non-repeatable reads, and phantoms are possible. Writers still take exclusive locks. |
| `READ COMMITTED` | Dirty reads are prevented, but each read releases its shared lock after the statement. Procedure 10 or 11 can change the row during the delay, causing a non-repeatable read. |
| `REPEATABLE READ` | An existing row read by Procedure 9 stays locked until commit, so writers wait and both reads match. Phantoms remain possible in general because missing ranges are not protected. |
| `SNAPSHOT` | Procedure 9 reads one stable version without blocking writers. Competing writers on the same row can cause an update conflict; the loser rolls back and retries. |
| `SERIALIZABLE` | Rows and key ranges stay locked until commit. Dirty reads, non-repeatable reads, and phantoms are prevented, but blocking and deadlock risk are highest. |

For a competing `DELETE` and `UPDATE` under locking isolation:

- If the update commits first, the delete later removes the updated row.
- If the delete commits first, the later update affects zero rows.
- Under `SNAPSHOT`, one conflicting writer can fail instead of waiting.
- Use a consistent table-access order, short transactions, and retry deadlock or snapshot-conflict victims.

`SNAPSHOT` is a strong choice for Procedure 9 because it gives consistent nonblocking reads. Short `READ COMMITTED` transactions are reasonable for Procedures 10 and 11.

## Question 13

For each club, find the training program or programs with the greatest number of distinct athletes who passed. Include ties.

```sql
SELECT
    ranked.club_id,
    ranked.club_name,
    ranked.program_id,
    ranked.program_name,
    ranked.passed_athlete_count
FROM
(
    SELECT
        club.club_id,
        club.club_name,
        program.program_id,
        program.program_name,
        COUNT(DISTINCT performance.athlete_id) AS passed_athlete_count,
        RANK() OVER (
            PARTITION BY club.club_id
            ORDER BY COUNT(DISTINCT performance.athlete_id) DESC
        ) AS program_rank
    FROM CLUB AS club
    JOIN TRAINING_PROGRAM AS program
        ON program.club_id = club.club_id
    LEFT JOIN TRAINING_SESSION AS session
        ON session.program_id = program.program_id
    LEFT JOIN PERFORMANCE AS performance
        ON performance.session_id = session.session_id
       AND performance.score_100 >= 50
    GROUP BY
        club.club_id,
        club.club_name,
        program.program_id,
        program.program_name
) AS ranked
WHERE ranked.program_rank = 1
ORDER BY ranked.club_id, ranked.program_id;
```

The `LEFT JOIN` includes programs with zero passing athletes. `RANK()` finds the maximum independently inside each club.

## Question 14

Find athletes who passed every direct prerequisite of at least one program but never enrolled in that target program.

```sql
SELECT
    athlete.athlete_id,
    athlete.athlete_name,
    target_program.program_id,
    target_program.program_name
FROM ATHLETE AS athlete
JOIN PERFORMANCE AS passed_performance
    ON passed_performance.athlete_id = athlete.athlete_id
JOIN TRAINING_SESSION AS prerequisite_session
    ON prerequisite_session.session_id = passed_performance.session_id
JOIN PROGRAM_PREREQUISITE AS prerequisite
    ON prerequisite.prerequisite_id = prerequisite_session.program_id
JOIN TRAINING_PROGRAM AS target_program
    ON target_program.program_id = prerequisite.program_id
WHERE passed_performance.score_100 >= 50
  AND NOT EXISTS (
      SELECT 1
      FROM TRAINING_SESSION AS target_session
      JOIN PERFORMANCE AS target_performance
        ON target_performance.session_id = target_session.session_id
      WHERE target_session.program_id = target_program.program_id
        AND target_performance.athlete_id = athlete.athlete_id
  )
GROUP BY
    athlete.athlete_id,
    athlete.athlete_name,
    target_program.program_id,
    target_program.program_name
HAVING COUNT(DISTINCT prerequisite.prerequisite_id) = (
    SELECT COUNT(*)
    FROM PROGRAM_PREREQUISITE AS all_prerequisites
    WHERE all_prerequisites.program_id = target_program.program_id
);
```

The `HAVING` comparison changes “passed at least one prerequisite” into “passed every direct prerequisite.”

## Question 15

Find coaches who coached at least one session of every program offered by their own club.

```sql
SELECT
    coach.coach_id,
    coach.coach_name,
    coach.club_id
FROM COACH AS coach
JOIN COACHING AS coaching
    ON coaching.coach_id = coach.coach_id
JOIN TRAINING_SESSION AS session
    ON session.session_id = coaching.session_id
JOIN TRAINING_PROGRAM AS program
    ON program.program_id = session.program_id
   AND program.club_id = coach.club_id
GROUP BY
    coach.coach_id,
    coach.coach_name,
    coach.club_id
HAVING COUNT(DISTINCT program.program_id) = (
    SELECT COUNT(*)
    FROM TRAINING_PROGRAM AS required_program
    WHERE required_program.club_id = coach.club_id
);
```

This is another relational-division query: programs covered must equal programs required.

## Question 16

Find sessions whose number of enrolled athletes exceeds capacity. Display the session, program, capacity, enrollment, and exceeded amount.

```sql
SELECT
    session.session_id,
    program.program_name,
    session.capacity,
    COUNT(performance.athlete_id) AS enrollment_count,
    COUNT(performance.athlete_id) - session.capacity AS exceeded_by
FROM TRAINING_SESSION AS session
JOIN TRAINING_PROGRAM AS program
    ON program.program_id = session.program_id
JOIN PERFORMANCE AS performance
    ON performance.session_id = session.session_id
GROUP BY
    session.session_id,
    program.program_name,
    session.capacity
HAVING COUNT(performance.athlete_id) > session.capacity;
```

No `ATHLETE` join or `DISTINCT` is needed because `(session_id, athlete_id)` is the primary key of `PERFORMANCE`.

## Question 17

Find same-club pairs of different athletes enrolled in exactly the same set of distinct programs. Display each pair once.

```sql
SELECT
    athlete1.athlete_id AS athlete1_id,
    athlete1.athlete_name AS athlete1_name,
    athlete2.athlete_id AS athlete2_id,
    athlete2.athlete_name AS athlete2_name,
    athlete1.club_id
FROM ATHLETE AS athlete1
JOIN ATHLETE AS athlete2
    ON athlete2.club_id = athlete1.club_id
   AND athlete1.athlete_id < athlete2.athlete_id
WHERE NOT EXISTS (
    SELECT 1
    FROM PERFORMANCE AS performance1
    JOIN TRAINING_SESSION AS session1
        ON session1.session_id = performance1.session_id
    WHERE performance1.athlete_id = athlete1.athlete_id
      AND NOT EXISTS (
          SELECT 1
          FROM PERFORMANCE AS performance2
          JOIN TRAINING_SESSION AS session2
              ON session2.session_id = performance2.session_id
          WHERE performance2.athlete_id = athlete2.athlete_id
            AND session2.program_id = session1.program_id
      )
)
AND NOT EXISTS (
    SELECT 1
    FROM PERFORMANCE AS performance2
    JOIN TRAINING_SESSION AS session2
        ON session2.session_id = performance2.session_id
    WHERE performance2.athlete_id = athlete2.athlete_id
      AND NOT EXISTS (
          SELECT 1
          FROM PERFORMANCE AS performance1
          JOIN TRAINING_SESSION AS session1
              ON session1.session_id = performance1.session_id
          WHERE performance1.athlete_id = athlete1.athlete_id
            AND session1.program_id = session2.program_id
      )
);
```

The first direction proves that athlete 1 has no program missing from athlete 2. The reverse direction proves the opposite subset. Both together prove set equality. The `<` condition removes reversed duplicate pairs.
