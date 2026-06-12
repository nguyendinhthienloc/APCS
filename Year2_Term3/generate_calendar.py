import datetime

events = [
    # CS426
    {
        "summary": "CS426 - Mobile Device Application Development (Theory)",
        "start": "20260601T093000",
        "end": "20260601T111000",
        "location": "Room E.307",
        "desc": "Lecturer: TM Triết",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    {
        "summary": "CS426 - Mobile Device Application Development (Theory)",
        "start": "20260603T093000",
        "end": "20260603T111000",
        "location": "Room I.23",
        "desc": "Lecturer: TM Triết",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    # CS486
    {
        "summary": "CS486 - Introduction to Database Systems (Theory)",
        "start": "20260601T133000",
        "end": "20260601T151000",
        "location": "Room I.35",
        "desc": "Lecturer: LT Nhân",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    {
        "summary": "CS486 - Introduction to Database Systems (Theory)",
        "start": "20260602T073000",
        "end": "20260602T091000",
        "location": "Room I.12C",
        "desc": "Lecturer: LT Nhân",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    {
        "summary": "CS486 - Introduction to Database Systems (Lab)",
        "start": "20260602T133000",
        "end": "20260602T153000",
        "location": "Room I.61",
        "desc": "Lecturers: NNM Châu, NN Toàn",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    # CS323
    {
        "summary": "CS323 - Social, Ethical, and Legal Issues (Theory)",
        "start": "20260601T153000",
        "end": "20260601T171000",
        "location": "Room I.35",
        "desc": "Lecturer: N Vũ",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    {
        "summary": "CS323 - Social, Ethical, and Legal Issues (Theory)",
        "start": "20260602T093000",
        "end": "20260602T111000",
        "location": "Room I.12C",
        "desc": "Lecturer: N Vũ",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    # MTH253
    {
        "summary": "MTH253 - Calculus III (Theory)",
        "start": "20260604T073000",
        "end": "20260604T111000",
        "location": "Room C.34",
        "desc": "Lecturer: NTH Thương",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    {
        "summary": "MTH253 - Calculus III (Lab)",
        "start": "20260603T073000",
        "end": "20260603T093000",
        "location": "Room I.34",
        "desc": "Lecturer: LV Chánh",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    # STAT452
    {
        "summary": "STAT452 - Applied Statistics for Engineers and Scientists II (Theory)",
        "start": "20260603T133000",
        "end": "20260603T171000",
        "location": "Room I.92",
        "desc": "Lecturer: HV Hà",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    {
        "summary": "STAT452 - Applied Statistics for Engineers and Scientists II (Lab)",
        "start": "20260606T093000",
        "end": "20260606T113000",
        "location": "Room I.12C",
        "desc": "Lecturer: HH Bình",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    },
    # BAA00022
    {
        "summary": "BAA00022 - Physical Education 2 (Theory)",
        "start": "20260605T073000",
        "end": "20260605T111000",
        "location": "TBD",
        "desc": "Lecturer: PTL Hằng",
        "rrule": "FREQ=WEEKLY;UNTIL=20260831T235959Z"
    }
]

ics_content = []
ics_content.append("BEGIN:VCALENDAR")
ics_content.append("VERSION:2.0")
ics_content.append("PRODID:-//Antigravity//Class Schedule//EN")
ics_content.append("CALSCALE:GREGORIAN")

# Define timezone Ho Chi Minh
ics_content.append("BEGIN:VTIMEZONE")
ics_content.append("TZID:Asia/Ho_Chi_Minh")
ics_content.append("BEGIN:STANDARD")
ics_content.append("DTSTART:19700101T000000")
ics_content.append("TZOFFSETFROM:+0700")
ics_content.append("TZOFFSETTO:+0700")
ics_content.append("TZNAME:+07")
ics_content.append("END:STANDARD")
ics_content.append("END:VTIMEZONE")

for i, event in enumerate(events):
    ics_content.append("BEGIN:VEVENT")
    ics_content.append(f"UID:event-{i}-24125093@apcs.hcmus.edu.vn")
    ics_content.append(f"DTSTAMP:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")
    ics_content.append(f"DTSTART;TZID=Asia/Ho_Chi_Minh:{event['start']}")
    ics_content.append(f"DTEND;TZID=Asia/Ho_Chi_Minh:{event['end']}")
    ics_content.append(f"RRULE:{event['rrule']}")
    ics_content.append(f"SUMMARY:{event['summary']}")
    ics_content.append(f"LOCATION:{event['location']}")
    ics_content.append(f"DESCRIPTION:{event['desc']}")
    ics_content.append("END:VEVENT")

ics_content.append("END:VCALENDAR")

with open("class_schedule.ics", "w", encoding="utf-8") as f:
    f.write("\n".join(ics_content))

print("ICS file generated successfully as class_schedule.ics")
