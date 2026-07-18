USE MidtermK22
GO
-- 1. Hotel Table
CREATE TABLE Hotel (
    HotelID VARCHAR(10) PRIMARY KEY,
    HotelName VARCHAR(100),
    Address VARCHAR(200)
);

-- 2. Workshop Table
CREATE TABLE Workshop (
    WorkshopID VARCHAR(10) PRIMARY KEY,
    WorkshopName VARCHAR(100),
    RegistrationFee DECIMAL(10,2)
);

-- 3. Workshop Session Table
CREATE TABLE WorkshopSession (
    SessionID VARCHAR(10) PRIMARY KEY,
    WorkshopID VARCHAR(10),
    HotelID VARCHAR(10),
    SessionDate DATE,
    PricePaidToHotel DECIMAL(10,2),
    ParticipantsCount INT,
    FOREIGN KEY (WorkshopID) REFERENCES Workshop(WorkshopID),
    FOREIGN KEY (HotelID) REFERENCES Hotel(HotelID)
);
