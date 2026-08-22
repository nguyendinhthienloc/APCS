# ER Diagram & Relational Schema — Mock Test 3 (Airline Flight System)

This file shows **both representations of the same database**:

1. **ER Diagram (conceptual model)** — entities, attributes, relationships, cardinalities.
2. **Relational Schema (logical/table model)** — tables, primary keys, foreign keys, and constraints.

> Note: Mermaid's built-in `erDiagram` uses Crow's Foot notation rather than classic Chen ovals/diamonds.  
> The first diagram below therefore uses a Mermaid `flowchart` to imitate **Chen notation**.

---

# 1. ER Diagram — Chen-Style

```mermaid
flowchart TB
    %% ENTITIES
    FLIGHT[FLIGHT]
    FLEG[FLIGHT_LEG]
    AIRPORT[AIRPORT]
    AIRCRAFT[AIRCRAFT]
    LINST[LEG_INSTANCE]

    %% RELATIONSHIPS
    CONS{consists of}
    ORIG{origin of}
    DEST{destination of}
    INST{instantiated as}
    USED{uses}

    %% ATTRIBUTES
    FNO([FNo — KEY])
    AL([Airline])

    LFNO([FNo — partial/key component])
    LNO([LegNo — partial/key component])

    ACODE([Code — KEY])
    CITY([City])

    ACID([AircraftID — KEY])
    CAP([Capacity])

    IFNO([FNo — partial/key component])
    ILNO([LegNo — partial/key component])
    IFD([FDate — partial/key component])
    SEATS([SeatsBooked])

    %% ENTITY ATTRIBUTES
    FLIGHT --- FNO
    FLIGHT --- AL

    FLEG --- LFNO
    FLEG --- LNO

    AIRPORT --- ACODE
    AIRPORT --- CITY

    AIRCRAFT --- ACID
    AIRCRAFT --- CAP

    LINST --- IFNO
    LINST --- ILNO
    LINST --- IFD
    LINST --- SEATS

    %% RELATIONSHIPS + CARDINALITIES
    FLIGHT ---|1| CONS
    CONS ---|1..N| FLEG

    AIRPORT ---|0..N| ORIG
    ORIG ---|1..1| FLEG

    AIRPORT ---|0..N| DEST
    DEST ---|1..1| FLEG

    FLEG ---|1| INST
    INST ---|0..N| LINST

    AIRCRAFT ---|0..N| USED
    USED ---|1..1| LINST
```

### Meaning

- **Flight & FlightLeg (`consists of`):** One **FLIGHT** consists of one or more **FLIGHT_LEG**s ($1:N$, total participation on `FLIGHT_LEG`). `FLIGHT_LEG` is existence-dependent on `FLIGHT`; leg numbers `1, 2, 3, ...` are scoped per flight.
- **Airport & FlightLeg (`origin of` & `destination of`):** Each **FLIGHT_LEG** has **exactly one** origin airport and **exactly one** destination airport ($1:N$ each). An **AIRPORT** can serve as the origin or destination for zero or more legs.
- **FlightLeg & LegInstance (`instantiated as`):** A **FLIGHT_LEG** is flown on specific dates as zero or more **LEG_INSTANCE**s ($1:N$). `LEG_INSTANCE` is existence-dependent on `FLIGHT_LEG`; identified by `(FNo, LegNo, FDate)`.
- **Aircraft & LegInstance (`uses`):** Each **LEG_INSTANCE** uses **exactly one** assigned **AIRCRAFT** ($1:N$). An aircraft can be used by zero or more leg instances across time.

---

# 2. Relational Schema — Tables, PKs and FKs

```mermaid
erDiagram
    FLIGHT ||--|{ FLIGHT_LEG : "consists_of (1:N)"
    AIRPORT ||--o{ FLIGHT_LEG : "origin_of (1:N)"
    AIRPORT ||--o{ FLIGHT_LEG : "destination_of (1:N)"
    FLIGHT_LEG ||--o{ LEG_INSTANCE : "instantiated_as (1:N)"
    AIRCRAFT ||--o{ LEG_INSTANCE : "used_by (1:N)"

    FLIGHT {
        string FNo PK
        string Airline
    }

    FLIGHT_LEG {
        string FNo PK, FK
        int LegNo PK
        string Orig FK
        string Dest FK
    }

    AIRPORT {
        string Code PK
        string City
    }

    AIRCRAFT {
        string AircraftID PK
        int Capacity
    }

    LEG_INSTANCE {
        string FNo PK, FK
        int LegNo PK, FK
        date FDate PK
        string AircraftID FK
        int SeatsBooked
    }
```

## Relational notation

### FLIGHT

**FLIGHT**(`FNo`, Airline)

- **PK:** `FNo`

### AIRPORT

**AIRPORT**(`Code`, City)

- **PK:** `Code`

### AIRCRAFT

**AIRCRAFT**(`AircraftID`, Capacity)

- **PK:** `AircraftID`

### FLIGHT_LEG

**FLIGHT_LEG**(`FNo`, `LegNo`, Orig, Dest)

- **PK:** (`FNo`, `LegNo`)
- **FK:** `FNo` → `FLIGHT(FNo)`
- `ON DELETE CASCADE`
- **FK:** `Orig` → `AIRPORT(Code)`
- `NOT NULL`
- **FK:** `Dest` → `AIRPORT(Code)`
- `NOT NULL`
- **CHECK:** `Orig <> Dest`
  - Origin and destination airports must differ.

### LEG_INSTANCE

**LEG_INSTANCE**(`FNo`, `LegNo`, `FDate`, AircraftID, SeatsBooked)

- **PK:** (`FNo`, `LegNo`, `FDate`)
- **FK:** (`FNo`, `LegNo`) → `FLIGHT_LEG(FNo, LegNo)`
- `ON DELETE CASCADE`
- **FK:** `AircraftID` → `AIRCRAFT(AircraftID)`
- `NOT NULL`

---

# Quick Exam Distinction

| ER Diagram | Relational Schema |
|---|---|
| Conceptual design | Logical/table design |
| Entity → rectangle | Relation → table |
| Attribute → oval | Attribute → column |
| Relationship → diamond | Relationship → foreign key |
| Shows 1:1, 1:N, M:N | Shows PK/FK references |
| Used before conversion | Result after ER-to-relational mapping |

**Memory rule:**

> **ER diagram:** What entities exist and how are they related?  
> **Relational schema:** What tables do I create, and what are their PKs/FKs?
