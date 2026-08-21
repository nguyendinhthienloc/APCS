USE SportsTrainingDB;
GO

/* ================================================================
   1. Programs with prerequisites whose prerequisites have none
   ================================================================ */

SELECT
    program.program_id,
    program.program_name
FROM dbo.TRAINING_PROGRAM AS program
WHERE EXISTS
(
    SELECT 1
    FROM dbo.PROGRAM_PREREQUISITE AS direct_prereq
    WHERE direct_prereq.program_id = program.program_id
)
AND NOT EXISTS
(
    SELECT 1
    FROM dbo.PROGRAM_PREREQUISITE AS direct_prereq
    JOIN dbo.PROGRAM_PREREQUISITE AS prereq_of_prereq
      ON prereq_of_prereq.program_id = direct_prereq.prerequisite_id
    WHERE direct_prereq.program_id = program.program_id
);
GO

/* ================================================================
   2. Coaches matching their head coach's season and year
   ================================================================ */

SELECT DISTINCT
    coach.coach_id,
    coach.coach_name
FROM dbo.COACH AS coach
JOIN dbo.CLUB AS club
    ON club.club_id = coach.club_id
JOIN dbo.COACHING AS coach_assignment
    ON coach_assignment.coach_id = coach.coach_id
JOIN dbo.TRAINING_SESSION AS coach_session
    ON coach_session.session_id = coach_assignment.session_id
JOIN dbo.COACHING AS head_assignment
    ON head_assignment.coach_id = club.head_coach_id
JOIN dbo.TRAINING_SESSION AS head_session
    ON head_session.session_id = head_assignment.session_id
WHERE head_session.season = coach_session.season
  AND head_session.training_year = coach_session.training_year;
GO

/* ================================================================
   3. Athletes who passed a program from every club
   ================================================================ */

SELECT
    athlete.athlete_id,
    athlete.athlete_name
FROM dbo.ATHLETE AS athlete
JOIN dbo.PERFORMANCE AS performance
    ON performance.athlete_id = athlete.athlete_id
JOIN dbo.TRAINING_SESSION AS session
    ON session.session_id = performance.session_id
JOIN dbo.TRAINING_PROGRAM AS program
    ON program.program_id = session.program_id
WHERE performance.score_100 >= 50
GROUP BY
    athlete.athlete_id,
    athlete.athlete_name
HAVING COUNT(DISTINCT program.club_id) =
(
    SELECT COUNT(*)
    FROM dbo.CLUB
);
GO

/* ================================================================
   4. Club or clubs with the highest average coach salary
   ================================================================ */

SELECT TOP (1) WITH TIES
    club.club_id,
    club.club_name,
    AVG(CAST(coach.salary AS DECIMAL(18, 2))) AS average_salary
FROM dbo.CLUB AS club
JOIN dbo.COACH AS coach
    ON coach.club_id = club.club_id
GROUP BY
    club.club_id,
    club.club_name
ORDER BY average_salary DESC;
GO

/* ================================================================
   5. Current enrollments with no direct prerequisite passed
   ================================================================ */

SELECT DISTINCT
    athlete.athlete_id,
    athlete.athlete_name
FROM dbo.ATHLETE AS athlete
JOIN dbo.PERFORMANCE AS current_performance
    ON current_performance.athlete_id = athlete.athlete_id
JOIN dbo.TRAINING_SESSION AS current_session
    ON current_session.session_id = current_performance.session_id
WHERE current_performance.score_100 IS NULL
  AND EXISTS
  (
      SELECT 1
      FROM dbo.PROGRAM_PREREQUISITE AS prerequisite
      WHERE prerequisite.program_id = current_session.program_id
  )
  AND NOT EXISTS
  (
      SELECT 1
      FROM dbo.PROGRAM_PREREQUISITE AS prerequisite
      JOIN dbo.TRAINING_SESSION AS prerequisite_session
        ON prerequisite_session.program_id = prerequisite.prerequisite_id
      JOIN dbo.PERFORMANCE AS prerequisite_performance
        ON prerequisite_performance.session_id = prerequisite_session.session_id
       AND prerequisite_performance.athlete_id = athlete.athlete_id
      WHERE prerequisite.program_id = current_session.program_id
        AND prerequisite_performance.score_100 >= 50
  );
GO

/* ================================================================
   6. Top coach or coaches in each club by unique programs coached
   ================================================================ */

WITH ProgramCounts AS
(
    SELECT
        club.club_id,
        club.club_name,
        coach.coach_id,
        coach.coach_name,
        COUNT(DISTINCT session.program_id) AS program_count
    FROM dbo.CLUB AS club
    JOIN dbo.COACH AS coach
        ON coach.club_id = club.club_id
    LEFT JOIN dbo.COACHING AS coaching
        ON coaching.coach_id = coach.coach_id
    LEFT JOIN dbo.TRAINING_SESSION AS session
        ON session.session_id = coaching.session_id
    GROUP BY
        club.club_id,
        club.club_name,
        coach.coach_id,
        coach.coach_name
),
MaximumCounts AS
(
    SELECT
        club_id,
        MAX(program_count) AS maximum_program_count
    FROM ProgramCounts
    GROUP BY club_id
)
SELECT
    counts.club_id,
    counts.club_name,
    counts.coach_id,
    counts.coach_name,
    counts.program_count
FROM ProgramCounts AS counts
JOIN MaximumCounts AS maximums
    ON maximums.club_id = counts.club_id
   AND maximums.maximum_program_count = counts.program_count;
GO

/* ================================================================
   7. Unique program names within each club

   Table of influence: TRAINING_PROGRAM
   Operations: INSERT and UPDATE
   ================================================================ */

CREATE OR ALTER TRIGGER dbo.same_program_name
ON dbo.TRAINING_PROGRAM
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS
    (
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

/* ================================================================
   8. Cascading club deletion trigger

   Directly or indirectly affected tables:
   CLUB, COACH, ATHLETE, TRAINING_PROGRAM, TRAINING_SESSION,
   COACHING, PERFORMANCE, and PROGRAM_PREREQUISITE.
   ================================================================ */

CREATE OR ALTER TRIGGER dbo.trg_DeleteClub
ON dbo.CLUB
INSTEAD OF DELETE
AS
BEGIN
    /* Remove all head-coach references to coaches being deleted. */
    UPDATE club
    SET head_coach_id = NULL
    FROM dbo.CLUB AS club
    JOIN dbo.COACH AS coach
        ON coach.coach_id = club.head_coach_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = coach.club_id;

    /* Delete performances belonging to the deleted clubs' athletes. */
    DELETE performance
    FROM dbo.PERFORMANCE AS performance
    JOIN dbo.ATHLETE AS athlete
        ON athlete.athlete_id = performance.athlete_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = athlete.club_id;

    /* Delete performances in the deleted clubs' sessions. */
    DELETE performance
    FROM dbo.PERFORMANCE AS performance
    JOIN dbo.TRAINING_SESSION AS session
        ON session.session_id = performance.session_id
    JOIN dbo.TRAINING_PROGRAM AS program
        ON program.program_id = session.program_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    /* Delete assignments belonging to the deleted clubs' coaches. */
    DELETE coaching
    FROM dbo.COACHING AS coaching
    JOIN dbo.COACH AS coach
        ON coach.coach_id = coaching.coach_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = coach.club_id;

    /* Delete assignments in the deleted clubs' sessions. */
    DELETE coaching
    FROM dbo.COACHING AS coaching
    JOIN dbo.TRAINING_SESSION AS session
        ON session.session_id = coaching.session_id
    JOIN dbo.TRAINING_PROGRAM AS program
        ON program.program_id = session.program_id
    JOIN deleted AS deleted_club
        ON deleted_club.club_id = program.club_id;

    /* Delete prerequisite relationships in either direction. */
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

/* ================================================================
   9. Read a score twice with a ten-second delay
   ================================================================ */

CREATE OR ALTER PROCEDURE Read_Score_Twice
    @athlete_id VARCHAR(10),
    @session_id INT
AS
BEGIN
    BEGIN TRANSACTION;

    SELECT score_100
    FROM PERFORMANCE
    WHERE athlete_id = @athlete_id
      AND session_id = @session_id;

    WAITFOR DELAY '00:00:10';

    SELECT score_100
    FROM PERFORMANCE
    WHERE athlete_id = @athlete_id
      AND session_id = @session_id;

    COMMIT TRANSACTION;
END;
GO

/* ================================================================
   10. Delete an athlete's performance record
   ================================================================ */

CREATE OR ALTER PROCEDURE delete_performance
    @athlete_id VARCHAR(10),
    @session_id INT
AS
BEGIN
    BEGIN TRANSACTION;

    IF NOT EXISTS
    (
        SELECT 1
        FROM ATHLETE
        WHERE athlete_id = @athlete_id
    )
    OR NOT EXISTS
    (
        SELECT 1
        FROM TRAINING_SESSION
        WHERE session_id = @session_id
    )
    BEGIN
        ROLLBACK TRANSACTION;
        RETURN;
    END;

    DELETE FROM PERFORMANCE
    WHERE athlete_id = @athlete_id
      AND session_id = @session_id;

    COMMIT TRANSACTION;
END;
GO

/* ================================================================
   11. Multiply an athlete's score by 1.1
   ================================================================ */

CREATE OR ALTER PROCEDURE multiply_athlete_score
    @athlete_id VARCHAR(10),
    @session_id INT
AS
BEGIN
    BEGIN TRANSACTION;

    IF EXISTS
    (
        SELECT 1
        FROM ATHLETE
        WHERE athlete_id = @athlete_id
    )
    AND EXISTS
    (
        SELECT 1
        FROM TRAINING_SESSION
        WHERE session_id = @session_id
    )
    BEGIN
        UPDATE PERFORMANCE
        SET score_100 = score_100 * 1.1
        WHERE athlete_id = @athlete_id
          AND session_id = @session_id;
    END;

    COMMIT TRANSACTION;
END;
GO

/* ================================================================
   12. Concurrency analysis: problems without additional controls

   Starting point
     The procedures use transactions, so each individual procedure is atomic.
     However, they do not choose an explicit isolation level, lock the target
     row in advance, define whether DELETE or UPDATE should win, or retry
     deadlocks/snapshot conflicts. SQL Server therefore uses the session's
     isolation level; normally this is READ COMMITTED. This is intentional so
     the caller can test the same procedures under each isolation level.

   Problems at the default READ COMMITTED level

   Procedure 9 with Procedure 11:
     P9 reads the old score, P11 updates and commits during the delay, and P9
     reads the new score. This is a non-repeatable read.

   Procedure 9 with Procedure 10:
     P9 reads the row, P10 deletes and commits during the delay, and P9's
     second SELECT returns no row. This is another non-repeatable read.

   Procedure 10 with Procedure 11:
     DELETE and UPDATE both require an exclusive lock, so they cannot modify
     the row simultaneously. One blocks and the order is unpredictable. If
     UPDATE commits first, DELETE later removes the updated row. If DELETE
     commits first, UPDATE later affects zero rows. The final row is deleted,
     but the update may be wasted.

   Two executions of Procedure 11:
     The UPDATE statements serialize and normally multiply the score twice.
     There is no lost update because score_100 = score_100 * 1.1 is one atomic
     UPDATE expression, although applying the adjustment twice may violate the
     intended business rule.

   All three procedures:
     P9 may see the old score, the updated score, or no row depending on the
     order. If P10 commits, the final state is no PERFORMANCE row.

   Isolation-level comparison

   READ UNCOMMITTED
     P9 can read P11's uncommitted score or observe an uncommitted delete that
     later rolls back: dirty reads. Its two reads can also differ. Writers
     still use exclusive locks, so DELETE and UPDATE still block each other.
     Control: do not use this level when the score must be trustworthy.

   READ COMMITTED
     Prevents dirty reads, but releases P9's shared lock after each SELECT.
     P10 or P11 can commit during the delay, causing a changed or missing
     second result. Control: use SNAPSHOT or hold the read lock longer when
     both results must describe one stable state.

   REPEATABLE READ
     P9 holds the shared lock on an existing row until commit, so P10 and P11
     wait through the ten-second delay and both reads match. It does not lock a
     missing key range, so a phantom insert is possible in general. These three
     procedures do not INSERT, so they cannot create a phantom by themselves.
     Cost: longer blocking.

   SNAPSHOT
     P9 reads the same row version twice without blocking P10 or P11. If P10
     and P11 both try to write the same row from overlapping snapshots, one
     writer can fail with an update-conflict error and must roll back and retry.

   SERIALIZABLE
     Holds row/key-range locks until commit. It prevents dirty reads,
     non-repeatable reads, and phantoms, but P9 can block writers for at least
     ten seconds. Blocking is highest and deadlocks are possible when other
     transactions acquire tables or rows in a different order.

   Required controls
     1. Keep both P9 reads inside one transaction.
     2. Choose SNAPSHOT for stable nonblocking reads, or REPEATABLE READ /
        SERIALIZABLE when blocking writers is acceptable.
     3. Keep P10 and P11 short and access tables in the same order.
     4. Check @@ROWCOUNT so callers know whether DELETE/UPDATE changed a row.
     5. Retry deadlock victims and SNAPSHOT update-conflict victims.
     6. If the business requires a fixed DELETE-versus-UPDATE winner, enforce
        that policy with stronger locking or an application-level rule.
   ================================================================ */

/* ================================================================
   13. Program or programs with the most passing athletes per club
   ================================================================ */

SELECT
    club.club_id,
    club.club_name,
    program.program_id,
    program.program_name,
    COUNT(DISTINCT performance.athlete_id) AS passed_athlete_count
FROM dbo.CLUB AS club
JOIN dbo.TRAINING_PROGRAM AS program
    ON program.club_id = club.club_id
LEFT JOIN dbo.TRAINING_SESSION AS session
    ON session.program_id = program.program_id
LEFT JOIN dbo.PERFORMANCE AS performance
    ON performance.session_id = session.session_id
   AND performance.score_100 >= 50
GROUP BY
    club.club_id,
    club.club_name,
    program.program_id,
    program.program_name
HAVING COUNT(DISTINCT performance.athlete_id) >= ALL
(
    SELECT COUNT(DISTINCT other_performance.athlete_id)
    FROM dbo.TRAINING_PROGRAM AS other_program
    LEFT JOIN dbo.TRAINING_SESSION AS other_session
        ON other_session.program_id = other_program.program_id
    LEFT JOIN dbo.PERFORMANCE AS other_performance
        ON other_performance.session_id = other_session.session_id
       AND other_performance.score_100 >= 50
    WHERE other_program.club_id = club.club_id
    GROUP BY other_program.program_id
)
ORDER BY club.club_id, program.program_id;
GO

/* ================================================================
   14. Passed every direct prerequisite but never enrolled in target
   ================================================================ */

SELECT
    athlete.athlete_id,
    athlete.athlete_name,
    target_program.program_id,
    target_program.program_name
FROM dbo.ATHLETE AS athlete
JOIN dbo.PERFORMANCE AS passed_performance
    ON passed_performance.athlete_id = athlete.athlete_id
JOIN dbo.TRAINING_SESSION AS prerequisite_session
    ON prerequisite_session.session_id = passed_performance.session_id
JOIN dbo.PROGRAM_PREREQUISITE AS prerequisite
    ON prerequisite.prerequisite_id = prerequisite_session.program_id
JOIN dbo.TRAINING_PROGRAM AS target_program
    ON target_program.program_id = prerequisite.program_id
WHERE passed_performance.score_100 >= 50
  AND NOT EXISTS
  (
      SELECT 1
      FROM dbo.TRAINING_SESSION AS target_session
      JOIN dbo.PERFORMANCE AS target_performance
        ON target_performance.session_id = target_session.session_id
      WHERE target_session.program_id = target_program.program_id
        AND target_performance.athlete_id = athlete.athlete_id
  )
GROUP BY
    athlete.athlete_id,
    athlete.athlete_name,
    target_program.program_id,
    target_program.program_name
HAVING COUNT(DISTINCT prerequisite.prerequisite_id) =
(
    SELECT COUNT(*)
    FROM dbo.PROGRAM_PREREQUISITE AS all_prerequisites
    WHERE all_prerequisites.program_id = target_program.program_id
);
GO

/* ================================================================
   15. Coaches who covered every program offered by their own club
   ================================================================ */

SELECT
    coach.coach_id,
    coach.coach_name,
    coach.club_id
FROM dbo.COACH AS coach
JOIN dbo.COACHING AS coaching
    ON coaching.coach_id = coach.coach_id
JOIN dbo.TRAINING_SESSION AS session
    ON session.session_id = coaching.session_id
JOIN dbo.TRAINING_PROGRAM AS program
    ON program.program_id = session.program_id
   AND program.club_id = coach.club_id
GROUP BY
    coach.coach_id,
    coach.coach_name,
    coach.club_id
HAVING COUNT(DISTINCT program.program_id) =
(
    SELECT COUNT(*)
    FROM dbo.TRAINING_PROGRAM AS required_program
    WHERE required_program.club_id = coach.club_id
);
GO

/* ================================================================
   16. Sessions whose enrollment exceeds capacity
   ================================================================ */

SELECT
    session.session_id,
    program.program_name,
    session.capacity,
    COUNT(performance.athlete_id) AS enrollment_count,
    COUNT(performance.athlete_id) - session.capacity AS exceeded_by
FROM dbo.TRAINING_SESSION AS session
JOIN dbo.TRAINING_PROGRAM AS program
    ON program.program_id = session.program_id
JOIN dbo.PERFORMANCE AS performance
    ON performance.session_id = session.session_id
GROUP BY
    session.session_id,
    program.program_name,
    session.capacity
HAVING COUNT(performance.athlete_id) > session.capacity;
GO

/* ================================================================
   17. Same-club athlete pairs with identical program sets
   ================================================================ */

SELECT
    athlete1.athlete_id AS athlete1_id,
    athlete1.athlete_name AS athlete1_name,
    athlete2.athlete_id AS athlete2_id,
    athlete2.athlete_name AS athlete2_name,
    athlete1.club_id
FROM dbo.ATHLETE AS athlete1
JOIN dbo.ATHLETE AS athlete2
    ON athlete2.club_id = athlete1.club_id
   AND athlete1.athlete_id < athlete2.athlete_id
WHERE NOT EXISTS
(
    SELECT 1
    FROM dbo.PERFORMANCE AS performance1
    JOIN dbo.TRAINING_SESSION AS session1
        ON session1.session_id = performance1.session_id
    WHERE performance1.athlete_id = athlete1.athlete_id
      AND NOT EXISTS
      (
          SELECT 1
          FROM dbo.PERFORMANCE AS performance2
          JOIN dbo.TRAINING_SESSION AS session2
              ON session2.session_id = performance2.session_id
          WHERE performance2.athlete_id = athlete2.athlete_id
            AND session2.program_id = session1.program_id
      )
)
AND NOT EXISTS
(
    SELECT 1
    FROM dbo.PERFORMANCE AS performance2
    JOIN dbo.TRAINING_SESSION AS session2
        ON session2.session_id = performance2.session_id
    WHERE performance2.athlete_id = athlete2.athlete_id
      AND NOT EXISTS
      (
          SELECT 1
          FROM dbo.PERFORMANCE AS performance1
          JOIN dbo.TRAINING_SESSION AS session1
              ON session1.session_id = performance1.session_id
          WHERE performance1.athlete_id = athlete1.athlete_id
            AND session1.program_id = session2.program_id
      )
);
GO
