with Wins as (
    -- Case A: team was Team1 and won
    select m.Team1ID as TeamID, m.MatchID
    from Match m
    where m.ScoreTeam1 > m.ScoreTeam2

    union all

    -- Case B: team was Team2 and won
    select m.Team2ID as TeamID, m.MatchID
    from Match m  
    where m.ScoreTeam2 > m.ScoreTeam1
),
TeamWinCounts as (
    select t.TeamID, t.TeamName, count(w.MatchID) as TotalWins
    from Team t
    left join Wins w on w.TeamID = t.TeamID
    group by t.TeamID, t.TeamName
)
select TeamID, TeamName, TotalWins
from TeamWinCounts
where TotalWins = (select min(TotalWins) from TeamWinCounts);