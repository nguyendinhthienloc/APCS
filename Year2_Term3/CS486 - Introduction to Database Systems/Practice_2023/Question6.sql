CREATE TABLE PlayerTotalKills(
    PlayerID INT PRIMARY KEY,
    Nickname varchar(50),
    TotalKills int default 0 check (TotalKills >= 0)
    Foreign Key (PlayerID) references Player(PlayerID)
)

insert into PlayerTotalKills(PlayerID, NickName, TotalKills)
select p.PlayerID, p.Nickname, count(mp.Kills) as TotalKills
from Match m
join MatchPlayer mp on mp.MatchID = m.MatchID
join Player p on p.PlayerID = mp.PlayerID
group by p.PlayerID, p.Nickname
having count(mp.Kills) > 30;