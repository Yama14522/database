CREATE TABLE Kinds (
  KindID    int          NOT NULL AUTO_INCREMENT,
  Kind_Name nvarchar(10) NOT NULL,
  PRIMARY KEY (KindID)
);

CREATE TABLE Schedule_2(
  Dates             date          NOT NULL,
  User_Name         nvarchar(20)  NOT NULL,
  KindID            int           NOT NULL,
  Schedule_Contents nvarchar(255) NOT NULL,
  PRIMARY KEY (Dates, User_Name),
  FOREIGN KEY (KindID) REFERENCES Kinds(KindID)
)

INSERT INTO Kinds (Kind_Name) VALUES 
('学校'),('試験'),('課題'),
('行事'),('就活'),('アルバイト'),('旅行');
