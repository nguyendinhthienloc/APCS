

use EsportChampionShip
--1
Update MatchPlayer
set Role = 'Support'
where Role not in ('Support', 'Carry', 'Mid', 'Offlane', 'Hard Support')

ALTER TABLE MatchPlayer
add constraint CHK_MatchPlayer_Role CHECK(Role IN ('Support', 'Carry', 'Mid', 'Offlane', 'Hard Support'))

--2
select p.Nickname
from Match m
join MatchPlayer mp on m.MatchID = mp.MatchID
join Player p on mp.PlayerID = p.PlayerID
join Team t on p.TeamID = t.TeamID
where m.Date = '2025-05-24' 
and exists (select 1 from Team where (m.Team1ID = TeamID or m.Team2ID = TeamID) and TeamName = 'Vikings')
and t.TeamName <> 'Vikings'

--3 
select t.TeamID, p.PlayerID, p.Nickname
from Team t
join Player p on t.TeamID = p.TeamID
where not exists(
	select 1 from MatchPlayer m where p.PlayerID = m.PlayerID 
	and m.Role <> 'Support' 
	and m.Role <> 'Hard Support') 


--4
select p.PlayerID, p.Nickname, sum(m.Assists) as total_assists
from Player p
join MatchPlayer m on  p.PlayerID = m.PlayerID
where m.Role = 'Support'
group by p.PlayerID, p.Nickname
having sum(m.Assists) >= 30

--5
select  mp.MatchID, p.PlayerID, p.Nickname
from MatchPlayer mp
join Player p on mp.PlayerID = p.PlayerID
where mp.Kills =
(select max(mp2.Kills)
from MatchPlayer mp2 
where mp2.MatchID = mp.MatchID)

--6
create table PlayerTotalKills(
PlayerID INT PRIMARY KEY,
Nickname VARCHAR(50) UNIQUE,
TotalKills int,
foreign key (PlayerID) references Player(PlayerID)
)


INSERT INTO PlayerTotalKills (PlayerID, Nickname, TotalKills)
SELECT p.PlayerID, p.Nickname, SUM(m.Kills) AS TotalKills
FROM Player p
JOIN MatchPlayer m ON p.PlayerID = m.PlayerID
GROUP BY p.PlayerID, p.Nickname
HAVING SUM(m.Kills) > 30;


--7
;with num_win(TeamID, num) as( 
select Team1ID, count(MatchID)
from Match 
where ScoreTeam1 > ScoreTeam2
group by Team1ID

union all

select Team2ID, count(MatchID)
from Match
where ScoreTeam2 > ScoreTeam1
group by Team2ID
),
num_win_full(TeamID, TeamName, TotalWins) as(
select t.TeamID, t.TeamName, ISNULL(n.num, 0) 
from Team t
left join num_win n on t.TeamID = n.TeamID
)

select *
from num_win_full
where TotalWins = (select min(TotalWins) from num_win_full)




