USE SportsTrainingDB
GO
-- 1) Find the names of all training programs that have at least one prerequisite, but none of their prerequisite programs have prerequisites of their own.

-- SELECT tp.program_name, tp.program_id

-- FROM TRAINING_PROGRAM tp 
-- WHERE EXISTS (
--     SELECT p1.prerequisite_id
--     FROM PROGRAM_PREREQUISITE p1
--     WHERE tp.program_id = p1.program_id
-- )

-- AND NOT EXISTS(
--     SELECT *
--     FROM PROGRAM_PREREQUISITE p1
--     JOIN PROGRAM_PREREQUISITE p2
--     ON p1.prerequisite_id = p2.program_id
--     WHERE tp.program_id = p1.program_id
-- )
-- GO

--2)Identify all coaches who are coaching a training session in the same season and training year as the head coach of their own club.

-- SELECT coach.coach_id, coach.coach_name

-- FROM COACH 
-- JOIN CLUB on coach.club_id = club.club_id 
-- JOIN COACHING on coach.coach_id = coaching.coach_id
-- JOIN TRAINING_SESSION ts on coaching.session_id = ts.session_id
-- --join the table of head_coach
-- JOIN COACHING hc ON club.head_coach_id = hc.coach_id
-- JOIN TRAINING_SESSION tshc on hc.session_id = tshc.session_id

-- WHERE tshc.training_year = ts.training_year
-- AND tshc.season = ts.season\
-- GO

--3)Find all athletes who have taken and passed at least one training program offered by every club in the database.


SELECT athlete.athlete_id, athlete.athlete_name
FROM ATHLETE 
JOIN PERFORMANCE on athlete.athlete_id = performance.athlete_id
JOIN TRAINING_SESSION ts on performance.session_id = ts.session_id
JOIN TRAINING_PROGRAM tp on ts.program_id = tp.program_id
WHERE performance.score_100 >= 65

GROUP BY athlete.athlete_id, athlete.athlete_name
HAVING COUNT(DISTINCT tp.program_id) =
       (SELECT COUNT(*) FROM CLUB)

4)