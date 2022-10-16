import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the user app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        secure a connection with the database and stores it into the instance variable `conn`
        """
        self.conn = sqlite3.connect(
            "venmo.db", check_same_thread=False 
        )
        self.delete_user_table()
        self.delete_txns_table()
        self.create_user_table()
        self.create_transaction_table()
        

    def create_user_table(self):
        """
        create user table using SQL
        """
        self.conn.execute("""
        CREATE TABLE users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL,
        balance INTEGER
        );
        """)

    def create_transaction_table(self):
        """
        create transaction table using SQL
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS txns(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            sender_id INTEGER SECONDARY KEY NOT NULL,
            receiver_id INTEGER SECONDARY KEY NOT NULL,
            amount INTEGER NOT NULL,
            message TEXT,
            accepted BOOLEAN
        )
        """
        )

    def delete_user_table(self):
        """
        delete user table using SQL
        """
        self.conn.execute("DROP TABLE IF EXISTS users;")

    def delete_txns_table(self):
        """
        delete transaction table using SQL
        """
        self.conn.execute("DROP TABLE IF EXISTS txns;")

    def get_all_users(self):
        """
        return all user using SQL
        """
        cursor = self.conn.execute("SELECT * FROM users")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users
    
    def get_all_trans(self):
        cursor = self.conn.execute("SELECT * FROM txns")
        trans = []
        for row in cursor:
            trans.append({"id": row[0], "timestamp": row[1], "sender_id": row[2], 
            "receiver_id": row[3], "amount": row[4], "message": row[5], "accepted": row[6]})
        return trans

    def get_user_by_id(self, id):
        """
        Using SQL, gets a user by id
        """
        cursor = self.conn.execute("SELECT * FROM users WHERE id = ?", (id,))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None


    def insert_user_table(self, name, username, balance):
        """
        Using SQL, adds a new user in the user table
        """
        cursor = self.conn.execute("""
        INSERT INTO users (name, username, balance) 
        VALUES (?, ?, ?);
        """
        , (name, username, balance))
        
        self.conn.commit()
        return cursor.lastrowid

    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user by id
        """
        self.conn.execute("""
        DELETE FROM users
        WHERE id = ?;        
        """, (id,))
        self.conn.commit()

    def update_balance(self, user_id, amount):
        """
        Using SQL, update a user's balance by id
        """
        self.conn.execute(
            """
            UPDATE users
            SET balance = ?
            WHERE id = ?;
            """, (amount,user_id)
        )
        self.conn.commit()

    def insert_transaction(self, timestamp, sender_id, receiver_id, amount, message, accepted):
        """
        Using SQL, insert a transaction record to txn table
        """
        cursor = self.conn.execute("""
        INSERT INTO txns (timestamp, sender_id, receiver_id, amount, message, accepted) 
        VALUES (?, ?, ?, ?, ?, ?);
        """
        , (timestamp, sender_id, receiver_id, amount, message, accepted))
        
        self.conn.commit()
        return cursor.lastrowid

    def get_transaction_by_id(self, id):
        """
        Using SQL, get transacton by id
        """
        cursor = self.conn.execute("SELECT * FROM txns WHERE id = ?", (id,))
        for row in cursor:
            return {"id": row[0], "timestamp": row[1], "sender_id": row[2], 
            "receiver_id": row[3], "amount": row[4], "message": row[5], "accepted": row[6]}
        return None
    
    def update_transaction(self, id, now, accepted):
        """
        Using SQL, update transacton accepted attribute and timestamp
        """ 
        self.conn.execute(
            """
            UPDATE txns
            SET accepted = ?,
                timestamp = ?
            WHERE id = ?;
            """, (accepted,now,id)
        )
        self.conn.commit()

    def get_user_transactions(self, user_id):
        """
        Using SQL, get user transactions from txns table by id
        """    
        transactions = []
        cursor = self.conn.execute("SELECT * FROM txns WHERE sender_id = ?", (user_id,))
        for row in cursor:
            transactions.append({"id": row[0], "timestamp": row[1], "sender_id": row[2], 
            "receiver_id": row[3], "amount": row[4], "message": row[5], "accepted": row[6]})

        cursor = self.conn.execute("SELECT * FROM txns WHERE receiver_id = ?", (user_id,))
        for row in cursor:
            transactions.append({"id": row[0], "timestamp": row[1], "sender_id": row[2], 
            "receiver_id": row[3], "amount": row[4], "message": row[5], "accepted": row[6]})

        return transactions

# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
