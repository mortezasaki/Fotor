import sqlite3
import os
import sys
import utility
import datetime
import logging
from enums import *
from time import sleep

class Database:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('data.db', timeout=30.0)
        except sqlite3.OperationalError:
            sys.exit()
        except SystemExit:
            logging.info('Error in loading database...')
            sleep(1)
            sys.exit()

    def Create(self):
        c = self.conn.cursor()

        # Create account table
        c.execute('''CREATE TABLE account
                    (phonenumber text PRIMARY KEY,
                    username text,
                    country text,
                    firstname text,
                    family text,
                    gender INTEGER,
                    date_creation text,
                    status integer,
                    flood_wait_time text,
                    flood_wait_seconds integer)
                    ''')
        
        # Create joins table
        c.execute('''CREATE TABLE joins
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phonenumber text,
                    channel text,
                    date_join text,
                    FOREIGN KEY(phonenumber) REFERENCES account(phonenumber))
                    ''')

        # Create phone_issue table
        c.execute('''CREATE TABLE issues
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern INTEGER,
                    reason INTEGER,
                    ban_date text)
                ''')

        # Save (commit) the changes
        self.conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
    
    def NewAccount(self, phonenumber, username, country, firstname, family, gender):
        if utility.ValidatePhone(phonenumber):
            try:
                c = self.conn.cursor()
                command = "INSERT INTO account VALUES ('%s','%s','%s','%s','%s',%s,'%s',0,'None',0)" % (phonenumber, username, country, firstname, family, gender, datetime.datetime.now())
                c.execute(command)
                
                # Save (commit) the changes
                self.conn.commit()

                # We can also close the connection if we are done with it.
                # Just be sure any changes have been committed or they will be lost.
                return True
            except sqlite3.IntegrityError:
                return False
            except sqlite3.OperationalError:
                return False
            except Exception as e:
                logging.info(type(e).__name__)
                return False
        return False

    def Join(self, phonenumber, channel):
        if utility.ValidatePhone(phonenumber):
            try:
                c = self.conn.cursor()
                t = (phonenumber, channel, datetime.datetime.now(),)
                command = "INSERT INTO joins (phonenumber, channel, date_join) VALUES (?,?,?)"
                c.execute(command, t)
                
                # Save (commit) the changes
                self.conn.commit()

                # We can also close the connection if we are done with it.
                # Just be sure any changes have been committed or they will be lost.
                return True
            except sqlite3.OperationalError:
                return False
        return False

    # def DeleteAll(self):
    #         c = self.conn.cursor()
    #         c.execute("delete  from account")
    #         c.execute("delete  from joins")
    #         self.conn.commit()

    #         # We can also close the connection if we are done with it.
    #         # Just be sure any changes have been committed or they will be lost.
    #         self.conn.close()

    def NewIssue(self, phonenumber, reason):
        try:
            pattern = int(phonenumber[:4])
            c = self.conn.cursor()
            command = "INSERT INTO issues (pattern, reason, ban_date) VALUES ('%s','%s','%s')" % (pattern, reason, datetime.datetime.now())
            c.execute(command)
            
            # Save (commit) the changes
            self.conn.commit()

            # We can also close the connection if we are done with it.
            # Just be sure any changes have been committed or they will be lost.
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.OperationalError:
            return False
        except Exception as e:
            logging.info(type(e).__name__)
            return False

    def CountOfJoins(self, phonenumber):
        if utility.ValidatePhone(phonenumber):
            try:
                t = (phonenumber,)
                command = "Select * from joins where phonenumber=?"
                joins = self.conn.execute(command, t)
                res = len(joins.fetchall())
                return res
            except sqlite3.OperationalError:
                return 0
        return 0

    def UpdateStatus(self, phonenumber, status : int):
        try:
            command = "Update account set status = ? where phonenumber = ?"
            t = (status, phonenumber,)
            self.conn.execute(command, t)
            self.conn.commit()
            return True
        except sqlite3.OperationalError:
            return False

    def UpdateFlooWait(self, phonenumber, second : int):
        try:
            command = "Update account set flood_wait_time = ?, flood_wait_seconds = ? where phonenumber = ?"
            t = (datetime.datetime.now(), second, phonenumber,)
            self.conn.execute(command, t)
            self.conn.commit()
            return True    
        except sqlite3.OperationalError:
            return False            

    def GetUserName(self, phonenumber):
        command = "Select username from account where phonenumber=?"
        t = (phonenumber,)
        try:
            username = self.conn.execute(command, t)
            username = username.fetchone()[0]
            return username
        except TypeError:
            return None
        except KeyboardInterrupt: # fix issue 19
            username = self.conn.execute(command, t)
            username = username.fetchone()[0]
            return username
        except sqlite3.OperationalError:
            return None                        
        except Exception as e:
            logging.info(type(e).__name__)
            return None

    def GetIssues(self):
        try:
            command = 'Select * from issues'
            return self.conn.execute(command).fetchall()
        except sqlite3.OperationalError:
            return None
        except Exception as e:
            logging.info(type(e).__name__)
            return None

    def GetStatus(self, phonenumber):
        command = "Select status from account where phonenumber=?"
        t = (phonenumber,)
        try:
            status = self.conn.execute(command, t)
            count = status.fetchone()[0]
            return count
        except TypeError:
            return 1
        except KeyboardInterrupt: # fix issue 19
            status = self.conn.execute(command, t)
            count = status.fetchone()[0]
            return count
        except sqlite3.OperationalError:
            return 1                        
        except Exception as e:
            logging.info(type(e).__name__)
            return 1

    def GetFloodWait(self, phonenumber):
        command = "Select flood_wait_time, flood_wait_seconds from account where phonenumber=? and status = ?"
        t = (phonenumber, TelegramRegisterStats.FloodWait.value)
        try:
            status = self.conn.execute(command, t)
            return status.fetchone()
        except TypeError:
            return []
        except sqlite3.OperationalError:
            return []            
        except Exception as e:
            logging.info(type(e).__name__)
            return []

    def DeleteAccount(self, phonenumber):
        command = 'Delete from account where phonenumber = ?'
        t = (phonenumber,)
        try:
            deleted = self.conn.execute(command, t).rowcount
            self.conn.commit()
            return deleted
        except sqlite3.OperationalError:
            return False
        except Exception as e:
            logging.info(type(e).__name__)
            return False

    def Count(self, command, t):
        try:
            res = self.conn.execute(command, t)
            return len(res.fetchall())
        except sqlite3.OperationalError:
            return False
        except Exception as e:
            logging.info(type(e).__name__)
            return False

    def GetAccounts(self):
        try:
            command = 'Select * from account'
            return self.conn.execute(command).fetchall()
        except sqlite3.OperationalError:
            return None
        except Exception as e:
            logging.info(type(e).__name__)
            return None

    def Close(self):
        return self.conn.close()