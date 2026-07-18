-- Case A: Vikings is Team1 in the match -> opponent is Team2
USE EsportChampionship
select p.Nickname
from Match m
join Team t1 on t1.TeamID = m.Team1ID
join Team t2 on t2.TeamID = m.Team2ID
join Player p on p.TeamID = t2.TeamID
where t1.TeamName = 'Vikings'
  and m.Date = '2025-05-24'

union

-- Case B: Vikings is Team2 in the match -> opponent is Team1
select p.Nickname
from Match m
join Team t1 on t1.TeamID = m.Team1ID
join Team t2 on t2.TeamID = m.Team2ID
join Player p on p.TeamID = t1.TeamID
where t2.TeamName = 'Vikings'
  and m.Date = '2025-05-24';