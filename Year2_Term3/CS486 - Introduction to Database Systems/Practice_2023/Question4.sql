select p.playerID, p.Nickname, SUM(mp.Assists) as TotalAssists
from Player p
join MatchPlayer mp on p.PlayerID = mp.PlayerID
where mp.Role = 'Support'
group by p.PlayerID, p.Nickname
having SUM(mp.Assists) >= 30