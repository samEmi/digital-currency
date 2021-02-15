import sqlite3
from sqlite3 import Error
import os



def createConnection():
    if not os.path.exists("cold_wallet.db"):
        open("cold_wallet.db", "x").close()
    conn = None
    try:
        conn = sqlite3.connect("cold_wallet.db")
        return conn
    except Error as e:
        print(e)

    return conn

def sqlCreate(conn, SQLQuery):
    try:
        c = conn.cursor()
        c.execute(SQLQuery)
        conn.close()
    except Error as e:
        print(e)

def sqlSelect(conn, select):
    try:
        cur = conn.cursor()
        cur.execute(select)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(e)

def sqlInsert(conn, insert):
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid


# def checkWalletExists():





