USE SportsTrainingDB
GO
-- 1) Find the names of all training programs that have at least one prerequisite, but none of their prerequisite programs have prerequisites of their own.

SELECT tp.program_name, tp.program_id

FROM TRAINING_PROGRAM tp 
WHERE EXISTS (
    SELECT p1.prerequisite_id
    FROM PROGRAM_PREREQUISITE p1
    WHERE tp.program_id = p1.program_id
)

AND NOT EXISTS(
    SELECT *
    FROM PROGRAM_PREREQUISITE p1
    JOIN PROGRAM_PREREQUISITE p2
    ON p1.prerequisite_id = p2.program_id
    WHERE tp.program_id = p1.program_id
)
GO

-- 2)Identify all coaches who are coaching a training session in the same season and training year as the head coach of their own club.

SELECT DISTINCT coach.coach_id, coach.coach_name

FROM COACH 
JOIN CLUB on coach.club_id = club.club_id 
JOIN COACHING on coach.coach_id = coaching.coach_id
JOIN TRAINING_SESSION ts on coaching.session_id = ts.session_id
--join the table of head_coach
JOIN COACHING hc ON club.head_coach_id = hc.coach_id
JOIN TRAINING_SESSION tshc on hc.session_id = tshc.session_id

WHERE tshc.training_year = ts.training_year
AND tshc.season = ts.season
GO

-- 3)Find all athletes who have taken and passed at least one training program offered by every club in the database.


SELECT athlete.athlete_id, athlete.athlete_name
FROM ATHLETE 
JOIN PERFORMANCE on athlete.athlete_id = performance.athlete_id
JOIN TRAINING_SESSION ts on performance.session_id = ts.session_id
JOIN TRAINING_PROGRAM tp on ts.program_id = tp.program_id
WHERE performance.score_100 >= 50

GROUP BY athlete.athlete_id, athlete.athlete_name
HAVING COUNT(DISTINCT tp.club_id) =
       (SELECT COUNT(*) FROM CLUB)

-- 4) Find the club or clubs whose coaches have the highest average salary.

SELECT TOP 1 WITH TIES club.club_id, club_name, AVG(coach.salary)
FROM CLUB 
JOIN COACH ON club.club_id = coach.club_id

GROUP BY club.club_id, club_name
ORDER BY AVG(coach.salary) DESC

-- 5) Identify athletes who are currently enrolled in a training program but have not yet passed any of that program's prerequisites. Treat a PERFORMANCE row with a NULL score as a current enrollment.
SELECT DISTINCT
    a.athlete_id,
    a.athlete_name
FROM ATHLETE AS a
JOIN PERFORMANCE AS current_perf
    ON current_perf.athlete_id = a.athlete_id
JOIN TRAINING_SESSION AS current_session
    ON current_session.session_id = current_perf.session_id
JOIN TRAINING_PROGRAM AS current_program
    ON current_program.program_id = current_session.program_id
WHERE current_perf.score_100 IS NULL

  --The current program must actually have a prerequisite
  AND EXISTS (
      SELECT 1
      FROM PROGRAM_PREREQUISITE AS pp
      WHERE pp.program_id = current_program.program_id
  )

  -- The athlete must not have passed any prerequisite
  AND NOT EXISTS (
      SELECT 1
      FROM PROGRAM_PREREQUISITE AS pp
      JOIN TRAINING_SESSION AS prerequisite_session
          ON prerequisite_session.program_id = pp.prerequisite_id
      JOIN PERFORMANCE AS prerequisite_perf
          ON prerequisite_perf.session_id =
             prerequisite_session.session_id
         AND prerequisite_perf.athlete_id = a.athlete_id
      WHERE pp.program_id = current_program.program_id
        AND prerequisite_perf.score_100 >= 50
  );
GO 
-- 6)CTEs are allowed. For each club, find the coach who has coached the greatest number of unique training programs. Include ties.
WITH ProgramCounts AS (
    SELECT club.club_id, club.club_name, coach.coach_id, coach.coach_name, COUNT(DISTINCT ses.program_id) as program_count

    FROM CLUB JOIN COACH ON club.club_id = coach.club_id
    JOIN COACHING on coach.coach_id = coaching.coach_id
    JOIN TRAINING_SESSION ses on ses.session_id = coaching.session_id 

    GROUP BY club.club_id, club.club_name, coach.coach_id, coach.coach_name

)
,MaximumCounts AS (
    SELECT club_id, MAX(program_count) as max_sessions
    FROM ProgramCounts
    GROUP BY club_id
)

SELECT combined.club_id, combined.club_name, combined.coach_id, combined.coach_name, combined.program_count
FROM ProgramCounts combined
JOIN MaximumCounts max 
    ON combined.club_id = max.club_id
    AND combined.program_count  = max.max_sessions

--7)Identify the table of influence and write at least one trigger to enforce the following business rule:
GO
CREATE TRIGGER same_program_name
ON TRAINING_PROGRAM --This is the table of influence
AFTER INSERT, UPDATE --Operations 
AS

BEGIN 
  IF EXISTS (
    SELECT *
    FROM inserted as i
    JOIN TRAINING_PROGRAM as pr 
      ON i.club_id = pr.club_id 
      AND i.program_name = pr.program_name
    WHERE i.program_id <> pr.program_id
  )
  BEGIN
  ROLLBACK TRANSACTION
  RAISERROR ('2 different courses cannot have the same name', 16, 1) 
  END; 
END;


-- 8)  Write a trigger that performs a cascading delete when a club is deleted. The trigger must remove all dependent records without violating foreign-key constraints.

GO
CREATE TRIGGER trg_DeleteClub
ON CLUB
INSTEAD OF DELETE
AS
BEGIN
    -- 1. Remove references to coaches that will be deleted
    UPDATE c
    SET head_coach_id = NULL
    FROM CLUB c
    JOIN COACH co
        ON c.head_coach_id = co.coach_id
    JOIN deleted d
        ON co.club_id = d.club_id


    -- 2. Delete performance records

    -- Performances of athletes from the deleted clubs
    DELETE p
    FROM PERFORMANCE p
    JOIN ATHLETE a
        ON p.athlete_id = a.athlete_id
    JOIN deleted d
        ON a.club_id = d.club_id

    -- Performances in sessions belonging to the deleted clubs
    DELETE p
    FROM PERFORMANCE p
    JOIN TRAINING_SESSION s
        ON p.session_id = s.session_id
    JOIN TRAINING_PROGRAM tp
        ON s.program_id = tp.program_id
    JOIN deleted d
        ON tp.club_id = d.club_id


    -- 3. Delete coaching assignments

    -- Assignments of coaches from the deleted clubs
    DELETE cg
    FROM COACHING cg
    JOIN COACH co
        ON cg.coach_id = co.coach_id
    JOIN deleted d
        ON co.club_id = d.club_id

    -- Assignments in sessions belonging to the deleted clubs
    DELETE cg
    FROM COACHING cg
    JOIN TRAINING_SESSION s
        ON cg.session_id = s.session_id
    JOIN TRAINING_PROGRAM tp
        ON s.program_id = tp.program_id
    JOIN deleted d
        ON tp.club_id = d.club_id


    -- 4. Delete prerequisite relationships

    DELETE pp
    FROM PROGRAM_PREREQUISITE pp
    JOIN TRAINING_PROGRAM tp
        ON pp.program_id = tp.program_id
    JOIN deleted d
        ON tp.club_id = d.club_id

    DELETE pp
    FROM PROGRAM_PREREQUISITE pp
    JOIN TRAINING_PROGRAM tp
        ON pp.prerequisite_id = tp.program_id
    JOIN deleted d
        ON tp.club_id = d.club_id


    -- 5. Delete sessions
    DELETE s
    FROM TRAINING_SESSION s
    JOIN TRAINING_PROGRAM tp
        ON s.program_id = tp.program_id
    JOIN deleted d
        ON tp.club_id = d.club_id


    -- 6. Delete direct children of CLUB
    DELETE a
    FROM ATHLETE a
    JOIN deleted d
        ON a.club_id = d.club_id

    DELETE co
    FROM COACH co
    JOIN deleted d
        ON co.club_id = d.club_id

    DELETE tp
    FROM TRAINING_PROGRAM tp
    JOIN deleted d
        ON tp.club_id = d.club_id


    -- 7. Delete the clubs
    DELETE c
    FROM CLUB c
    JOIN deleted d
        ON c.club_id = d.club_id
END
GO

-- 9)Create a stored procedure that performs the following operations using a given <athlete_id> and <session_id>:
-- a. Read the athlete's current score_100 in the specified session.
-- b. Wait for 10 seconds.
-- c. Read the same score again.

GO
CREATE PROCEDURE Read_Score_Twice
    @athlete_id VARCHAR(20),
    @session_id INT 
AS 
BEGIN
  SELECT score_100
  FROM PERFORMANCE
  WHERE athlete_id = @athlete_id
  AND session_id = @session_id

WAITFOR DELAY '00:00:10';

SELECT score_100
  FROM PERFORMANCE
  WHERE athlete_id = @athlete_id
  AND session_id = @session_id;


END;
GO


--10)Create a stored procedure that deletes an athlete's performance record using a given <athlete_id> and <session_id>.

-- Input: athlete_id, session_id
-- Output: Roll back if either the athlete or the training session does not exist. Otherwise, delete the matching performance record and commit
DROP PROCEDURE IF EXISTS delete_performance
GO
CREATE PROCEDURE delete_performance
  @athlete_id VARCHAR(20),
  @session_id INT 
AS 
BEGIN 
BEGIN TRANSACTION;
  IF NOT EXISTS (
    SELECT 1 FROM ATHLETE
    WHERE athlete_id = @athlete_id
  )
  OR NOT EXISTS (
    SELECT 1 FROM TRAINING_SESSION
    where session_id = @session_id
  )
  BEGIN 
  ROLLBACK TRANSACTION;
  RETURN;
  END;


  BEGIN
  DELETE FROM PERFORMANCE
  WHERE athlete_id = @athlete_id
  AND session_id = @session_id
  END
COMMIT TRANSACTION;

END 

--11
CREATE PROCEDURE multiply_athlete_score
AS 
BEGIN
  IF EXISTS(
    SELECT 1 FROM athlete
    WHERE athlete_id = @athlete_id
  )
  OR (
    SELECT 1 FROM TRAINING_SESSION
    WHERE session_id = @session_id
  )

  ALTER TABLE PERFORMANCE 
  SET score_100 = score_100 * 1.1
  WHERE athlete_id = @athlete_id
  AND session_id = @session_id 

  COMMIT TRANSACTION;
END

--ADDTIONAL--
--13)For each club, find the training program or programs with the greatest number of distinct athletes who have passed the program. Include ties and display the club, program, and number of athletes who passed.
SELECT TOP 1 with ties club.club_id, pro.program_name, COUNT(DISTINCT performance.athlete_id) as no_passed_athletes
FROM CLUB 
JOIN ATHLETE on club.club_id = athlete.club_id
JOIN PERFORMANCE on athlete.athlete_id = performance.athlete_id
JOIN TRAINING_PROGRAM pro on club.club_id = pro.club_id
WHERE performance.score_100 > 50 
GROUP BY club.club_id, pro.program_name
ORDER BY no_passed_athletes DESC

--14)Find all athletes who have passed every prerequisite of at least one training program but have never enrolled in any session of that program. Return the athlete and the qualifying program
SELECT
    a.athlete_id,
    a.athlete_name,
    target_program.program_id,
    target_program.program_name
FROM ATHLETE AS a

-- Programs the athlete has passed
JOIN PERFORMANCE AS passed_perf
    ON passed_perf.athlete_id = a.athlete_id
JOIN TRAINING_SESSION AS prereq_session
    ON prereq_session.session_id = passed_perf.session_id

-- Target programs requiring those passed programs
JOIN PROGRAM_PREREQUISITE AS pp
    ON pp.prerequisite_id = prereq_session.program_id
JOIN TRAINING_PROGRAM AS target_program
    ON target_program.program_id = pp.program_id

WHERE passed_perf.score_100 >= 50

-- Athlete must never have enrolled in the target program
AND NOT EXISTS (
    SELECT 1
    FROM TRAINING_SESSION AS target_session
    JOIN PERFORMANCE AS target_perf
        ON target_perf.session_id = target_session.session_id
    WHERE target_session.program_id = target_program.program_id
      AND target_perf.athlete_id = a.athlete_id
)

GROUP BY
    a.athlete_id,
    a.athlete_name,
    target_program.program_id,
    target_program.program_name

-- Number of prerequisites passed must equal total prerequisites
HAVING COUNT(DISTINCT pp.prerequisite_id) = (
    SELECT COUNT(*)
    FROM PROGRAM_PREREQUISITE AS all_prereqs
    WHERE all_prereqs.program_id = target_program.program_id
);

--15)Find all coaches who have coached at least one session of every training program offered by their own club.


SELECT coach.coach_id, coach.coach_name
FROM COACH
JOIN COACHING on coach.coach_id = coaching.coach_id
JOIN TRANING_SESSION ses on ses.session_id = coaching.session_id
JOIN TRAINING_PROGRAM prog on prog.session_id = ses.session_id
AND coach.CLUB_id = ses.club_id
GROUP BY coach.coach_id, coach.coach_name
HAVING COUNT(DISTINCT tp.program_id) = (
    SELECT COUNT(*)
    FROM TRAINING_PROGRAM AS all_programs
    WHERE all_programs.club_id = c.club_id
);

--16)Find all training sessions whose number of enrolled athletes exceeds the session capacity. Display the session, program name, capacity, enrollment count, and the amount by which the capacity is exceeded.
USE SportsTrainingDB
GO
SELECT ses.session_id, ses.capacity, COUNT(DISTINCT athlete.athlete_id) as number_of_athletes
FROM TRAINING_SESSION ses 
JOIN TRAINING_PROGRAM prog on ses.program_id = prog.program_id
JOIN PERFORMANCE on ses.session_id = performance.session_id
JOIN ATHLETE on athlete.athlete_id = performance.athlete_id
GROUP BY ses.session_id, prog.program_name, ses.capacity
HAVING COUNT(DISTINCT athlete.athlete_id) > capacity

--17) Find pairs of different athletes from the same club who have enrolled in exactly the same set of distinct training programs. Display each pair only once.
SELECT
    a1.athlete_id   AS athlete1_id,
    a1.athlete_name AS athlete1_name,
    a2.athlete_id   AS athlete2_id,
    a2.athlete_name AS athlete2_name,
    a1.club_id
FROM ATHLETE a1 
JOIN ATHLETE a2 
    ON a2.club_id = a1.club_id 
    AND a1.athlete_id < a2.athlete_id 

--No program taken by 1 but not by 2
WHERE NOT EXISTS (
    SELECT 1
    FROM PERFORMANCE AS p1
    JOIN TRAINING_SESSION AS s1
        ON s1.session_id = p1.session_id
    WHERE p1.athlete_id = a1.athlete_id
      AND NOT EXISTS (
          SELECT 1
          FROM PERFORMANCE AS p2
          JOIN TRAINING_SESSION AS s2
              ON s2.session_id = p2.session_id
          WHERE p2.athlete_id = a2.athlete_id
            AND s2.program_id = s1.program_id
      )
)
AND NOT EXISTS (
    SELECT 1
    FROM PERFORMANCE AS p2
    JOIN TRAINING_SESSION AS s2
        ON s2.session_id = p2.session_id
    WHERE p2.athlete_id = a2.athlete_id
      AND NOT EXISTS (
          SELECT 1
          FROM PERFORMANCE AS p1
          JOIN TRAINING_SESSION AS s1
              ON s1.session_id = p1.session_id
          WHERE p1.athlete_id = a1.athlete_id
            AND s1.program_id = s2.program_id
      )
);