import enum

class RegisterAPIStatus(enum.Enum):
    Succesfull = 200
    AlreadyJoined = 201

class Gender(enum.Enum):
    Man = 0
    Woman = 1

class TelegramRegisterStats(enum.Enum):
    Succesfull = 1 
    Ban = 2
    FloodWait = 3
    HasPassword = 4
    Running = 5
    Stop = 6

class SMSActivateSMSStatus(enum.Enum):
    Report = 1
    AnotherCode = 3
    Complate = 6
    Cancel = 8