-- Hotels
INSERT INTO Hotel VALUES
('H03', 'Seaside Resort', '89 Ocean Drive'),
('H04', 'Mountain View Lodge', '12 Highland Rd'),
('H05', 'Airport Suites', '55 Terminal Blvd'),
('H06', 'Riverside Hotel', '101 Riverbank Ave'),
('H07', 'Green Garden Inn', '77 Garden St'),
('H08', 'Royal Palace Hotel', '999 King Ave'),
('H09', 'Sunset Retreat', '14 Sunset Blvd'),
('H10', 'Tech Convention Hotel', '250 Innovation Way');

INSERT INTO Workshop VALUES
('W03', 'Advanced SQL Queries', 90.00),
('W04', 'Database Design Essentials', 65.00),
('W05', 'Cloud Computing Basics', 80.00),
('W06', 'Python for Data Analysis', 95.00),
('W07', 'Machine Learning Foundations', 120.00),
('W08', 'Cybersecurity Awareness', 55.00),
('W09', 'Power BI Dashboard Design', 85.00),
('W10', 'Big Data with Hadoop', 130.00);

INSERT INTO WorkshopSession VALUES
('S4',  'W03', 'H03', '2024-08-18', 2500.00, 50),
('S5',  'W04', 'H04', '2024-09-02', 1800.00, 45),
('S6',  'W05', 'H05', '2024-09-15', 3500.00, 80),
('S7',  'W06', 'H06', '2024-10-01', 2700.00, 35),
('S8',  'W07', 'H07', '2024-10-20', 5000.00, 25),
('S9',  'W08', 'H08', '2024-11-05', 1600.00, 100),
('S10', 'W09', 'H09', '2024-11-18', 3200.00, 55);