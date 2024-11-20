-- Create the main database
CREATE DATABASE URGAS;
USE URGAS;

-- Professors Table
CREATE TABLE Professors (
    ProfessorID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Department VARCHAR(100),
    Email VARCHAR(100) UNIQUE NOT NULL
);

-- Funding Agencies Table
CREATE TABLE FundingAgencies (
    AgencyID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL UNIQUE,
    Budget DECIMAL(15, 2) NOT NULL
);

-- Grants Table
CREATE TABLE Grants (
    GrantID INT AUTO_INCREMENT PRIMARY KEY,
    Amount DECIMAL(15, 2) NOT NULL,
    FundingAgencyID INT NOT NULL,
    FOREIGN KEY (FundingAgencyID) REFERENCES FundingAgencies(AgencyID) 
        ON DELETE CASCADE
);

-- Projects Table
CREATE TABLE Projects (
    ProjectID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(200) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE
);

-- Projects_Grants (Many-to-Many relationship between Projects and Grants)
CREATE TABLE Projects_Grants (
    ProjectID INT NOT NULL,
    GrantID INT NOT NULL,
    PRIMARY KEY (ProjectID, GrantID),
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
        ON DELETE CASCADE,
    FOREIGN KEY (GrantID) REFERENCES Grants(GrantID)
        ON DELETE CASCADE
);

-- Professors_Projects (Many-to-Many relationship between Professors and Projects)
CREATE TABLE Professors_Projects (
    ProfessorID INT NOT NULL,
    ProjectID INT NOT NULL,
    PRIMARY KEY (ProfessorID, ProjectID),
    FOREIGN KEY (ProfessorID) REFERENCES Professors(ProfessorID)
        ON DELETE CASCADE,
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
        ON DELETE CASCADE
);

-- Publications Table
CREATE TABLE Publications (
    PublicationID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(200) NOT NULL,
    ProjectID INT UNIQUE, -- One-to-One relationship with Projects
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
        ON DELETE CASCADE
);

-- ProjectAudit Table for Historical Records
CREATE TABLE ProjectAudit (
    AuditID INT AUTO_INCREMENT PRIMARY KEY,
    ProjectID INT,
    Title VARCHAR(200),
    StartDate DATE,
    EndDate DATE,
    Action VARCHAR(50), -- e.g., 'Deleted', 'Updated'
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to Log Deleted Projects
DELIMITER $$
CREATE TRIGGER LogProjectDeletion
BEFORE DELETE ON Projects
FOR EACH ROW
BEGIN
    INSERT INTO ProjectAudit (ProjectID, Title, StartDate, EndDate, Action)
    VALUES (OLD.ProjectID, OLD.Title, OLD.StartDate, OLD.EndDate, 'Deleted');
END$$
DELIMITER ;

-- Trigger to Log Updated Projects
DELIMITER $$
CREATE TRIGGER LogProjectUpdate
BEFORE UPDATE ON Projects
FOR EACH ROW
BEGIN
    INSERT INTO ProjectAudit (ProjectID, Title, StartDate, EndDate, Action)
    VALUES (OLD.ProjectID, OLD.Title, OLD.StartDate, OLD.EndDate, 'Updated');
END$$
DELIMITER ;

-- Trigger to Assign Default Funding Agency to Grants
DELIMITER $$
CREATE TRIGGER DefaultFundingAgency
BEFORE INSERT ON Grants
FOR EACH ROW
BEGIN
    IF NEW.FundingAgencyID IS NULL THEN
        SET NEW.FundingAgencyID = (
            SELECT AgencyID FROM FundingAgencies 
            LIMIT 1
        );
    END IF;
END$$
DELIMITER ;

-- Trigger to Auto-Adjust Funding Agency Budget
DELIMITER $$
CREATE TRIGGER AdjustAgencyBudget
AFTER INSERT ON Grants
FOR EACH ROW
BEGIN
    UPDATE FundingAgencies
    SET Budget = Budget - NEW.Amount
    WHERE AgencyID = NEW.FundingAgencyID;
END$$
DELIMITER ;

-- Trigger to Prevent Duplicate Professors by Email
DELIMITER $$
CREATE TRIGGER PreventDuplicateProfessors
BEFORE INSERT ON Professors
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Professors WHERE Email = NEW.Email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Duplicate professor email not allowed.';
    END IF;
END$$
DELIMITER ;

-- Stored Procedure to Convert Project into Publication
DELIMITER $$
CREATE PROCEDURE ConvertProjectToPublication(IN project_id INT, IN publication_title VARCHAR(255))
BEGIN
    -- Check if the project exists
    IF EXISTS (SELECT 1 FROM Projects WHERE ProjectID = project_id) THEN
        -- Insert into Publications table
        INSERT INTO Publications (Title , ProjectID)
        VALUES (publication_title, project_id);

        -- Delete the specific project
        DELETE FROM Projects WHERE ProjectID = project_id;

    ELSE
        -- Signal an error if the project does not exist
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Project not found or already converted to Publication.';
    END IF;
END$$
DELIMITER ;

-- Stored Procedure to Assign Grant to Project
DELIMITER $$
CREATE PROCEDURE AssignGrantToProject(
    IN ProjectID INT,
    IN GrantID INT
)
BEGIN
    -- Check if the association already exists
    IF EXISTS (SELECT 1 FROM Projects_Grants WHERE ProjectID = ProjectID AND GrantID = GrantID) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This grant is already assigned to the project.';
    ELSE
        -- Insert the association into Projects_Grants
        INSERT INTO Projects_Grants (ProjectID, GrantID)
        VALUES (ProjectID, GrantID);
    END IF;
END$$
DELIMITER ;

-- Stored Procedure to Delete Professor and Their Solely Associated Projects
DELIMITER $$
CREATE PROCEDURE DeleteProfessorAndProjects(
    IN ProfessorID INT
)
BEGIN
    -- Delete projects where the professor is the only one working
    DELETE FROM Projects 
    WHERE ProjectID IN (
        SELECT ProjectID 
        FROM Professors_Projects 
        WHERE ProfessorID = ProfessorID 
        GROUP BY ProjectID
        HAVING COUNT(ProfessorID) = 1
    );

    -- Delete the professor
    DELETE FROM Professors WHERE ProfessorID = ProfessorID;
END$$
DELIMITER ;

-- View to List Professors and Their Active Projects
CREATE VIEW ProfessorProjects AS
SELECT 
    p.ProfessorID, 
    p.Name AS ProfessorName, 
    pr.ProjectID, 
    pr.Title AS ProjectTitle
FROM 
    Professors p
JOIN 
    Professors_Projects pp ON p.ProfessorID = pp.ProfessorID
JOIN 
    Projects pr ON pp.ProjectID = pr.ProjectID;

-- View to List Projects with Grants and Funding Agencies
CREATE VIEW ProjectGrantsFunding AS
SELECT 
    pg.ProjectID,
    pr.Title AS ProjectTitle,
    g.GrantID,
    g.Amount AS GrantAmount,
    fa.AgencyID,
    fa.Name AS FundingAgencyName
FROM 
    Projects_Grants pg
JOIN 
    Projects pr ON pg.ProjectID = pr.ProjectID
JOIN 
    Grants g ON pg.GrantID = g.GrantID
JOIN 
    FundingAgencies fa ON g.FundingAgencyID = fa.AgencyID;

-- View to List Professors Without Projects
CREATE VIEW ProfessorsWithoutProjects AS
SELECT 
    p.ProfessorID,
    p.Name AS ProfessorName
FROM 
    Professors p
LEFT JOIN 
    Professors_Projects pp ON p.ProfessorID = pp.ProfessorID
WHERE 
    pp.ProjectID IS NULL;

-- Deduct Grant Amount Procedure
DELIMITER $$
CREATE PROCEDURE DeductGrantAmount(IN grant_id INT, IN used_amount DECIMAL(15, 2))
BEGIN
    DECLARE current_amount DECIMAL(15, 2);

    -- Get the current grant amount
    SELECT Amount INTO current_amount
    FROM Grants
    WHERE GrantID = grant_id;

    -- Check if the grant exists
    IF current_amount IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Grant not found.';
    END IF;

    -- Deduct the amount
    SET current_amount = current_amount - used_amount;

    -- Update or delete the grant
    IF current_amount = 0 THEN
        DELETE FROM Grants WHERE GrantID = grant_id;
    ELSEIF current_amount < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "Amount exceeds remaining grant budget."
    ELSE
        UPDATE Grants SET Amount = current_amount WHERE GrantID = grant_id;
    END IF;
END$$
DELIMITER ;