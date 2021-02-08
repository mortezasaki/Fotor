import sqlite3
import os
import utility
import datetime
import logging

class Database:
    def __init__(self):
        if os.path.exists('data.db'):
            self.conn = sqlite3.connect('data.db')
        else:
            print(r"Can't find data.db file please run `createdb` command")

    def Create(self):
        c = self.conn.cursor()

        # Create table
        c.execute('''CREATE TABLE account
                    (phonenumber text PRIMARY KEY,
                    country text,
                    firstname text,
                    family text,
                    gender INTEGER,
                    date_creation text,
                    status integer)
                    ''')
        
        c.execute('''CREATE TABLE joins
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phonenumber text,
                    channel text,
                    date_join text,
                    FOREIGN KEY(phonenumber) REFERENCES account(phonenumber))
                    ''')


        # Save (commit) the changes
        self.conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
    
    def NewAccount(self, phonenumber, country, firstname, family, gender):
        if utility.ValidatePhone(phonenumber):
            try:
                c = self.conn.cursor()
                command = "INSERT INTO account VALUES ('%s','%s','%s','%s',%s,'%s',0)" % (phonenumber, country, firstname, family, gender, datetime.datetime.now())
                c.execute(command)
                
                # Save (commit) the changes
                self.conn.commit()

                # We can also close the connection if we are done with it.
                # Just be sure any changes have been committed or they will be lost.
                return True
            except sqlite3.IntegrityError:
                return False
        return False

    def Join(self, phonenumber, channel):
        if utility.ValidatePhone(phonenumber):
            c = self.conn.cursor()
            t = (phonenumber, channel, datetime.datetime.now(),)
            command = "INSERT INTO joins (phonenumber, channel, date_join) VALUES (?,?,?)"
            c.execute(command, t)
            
            # Save (commit) the changes
            self.conn.commit()

            # We can also close the connection if we are done with it.
            # Just be sure any changes have been committed or they will be lost.
            return True
        return False

    # def DeleteAll(self):
    #         c = self.conn.cursor()
    #         c.execute("delete  from account")
    #         c.execute("delete  from joins")
    #         self.conn.commit()

    #         # We can also close the connection if we are done with it.
    #         # Just be sure any changes have been committed or they will be lost.
    #         self.conn.close()

    def CountOfJoins(self, phonenumber):
        if utility.ValidatePhone(phonenumber):
            t = (phonenumber,)
            command = "Select * from joins where phonenumber=?"
            joins = self.conn.execute(command, t)
            res = len(joins.fetchall())
            return res
        return 0

    def UpdateStatus(self, phonenumber, status : int):
        command = "Update account set status = ? where phonenumber = ?"
        t = (status, phonenumber,)
        self.conn.execute(command, t)
        self.conn.commit()
        return True

    def GetStatus(self, phonenumber):
        command = "Select status from account where phonenumber=?"
        t = (phonenumber,)
        try:
            status = self.conn.execute(command, t)
            count = status.fetchone()[0]
            return count
        except TypeError:
            return 1
        except Exception as e:
            logging.info(type(e).__name__)
            return 1

    def DeleteAccount(self, phonenumber):
        command = 'Delete from account where phonenumber = ?'
        t = (phonenumber,)
        try:
            deleted = self.conn.execute(command, t).rowcount
            self.conn.commit()
            return deleted
        except Exception as e:
            logging.info(type(e).__name__)
            return False

    def Count(self, command, t):
        try:
            res = self.conn.execute(command, t)
            return len(res.fetchall())
        except Exception as e:
            logging.info(type(e).__name__)
            return False

    def Close(self):
        return self.conn.close()