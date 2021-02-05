import sqlite3
import os
import utility
import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('data.db')

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
        self.conn.close()
    
    def NewAccount(self, phonenumber, country, firstname, family, gender):
        if utility.ValidatePhone(phonenumber):
            c = self.conn.cursor()
            c.execute("INSERT INTO account VALUES ({phonenumber},{country},{firstname},{family},{gender},{datetime.datetime.now()})")
            
            # Save (commit) the changes
            self.conn.commit()

            # We can also close the connection if we are done with it.
            # Just be sure any changes have been committed or they will be lost.
            self.conn.close()
            return True
        return False

    def Join(self, phonenumber, channel):
        if utility.ValidatePhone(phonenumber):
            c = conn.cursor()
            c.execute("INSERT INTO joins VALUES ({phonenumber},{channel},{datetime.datetime.now()})")
            
            # Save (commit) the changes
            self.conn.commit()

            # We can also close the connection if we are done with it.
            # Just be sure any changes have been committed or they will be lost.
            self.conn.close()
            return True
        return False