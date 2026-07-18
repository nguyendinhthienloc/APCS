select h.hotelname, h.address, sum(ws.pricepaidtohotel) as total_revenue 
from hotel h 
left join workshopsession ws on h.hotelID = ws.HotelID 
group by h.hotelname, h.address, h.HotelID
order by h.hotelname asc, total_revenue desc