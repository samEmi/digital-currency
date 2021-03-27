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

def sqlInsert(conn, sql, values):
    try:
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        conn.close()
        return cur.lastrowid
    except Error as e:
        print(e)

def sqlDelete(conn, sql, values):
    try:
        for value in values:
            tk = (value,)
            cur = conn.cursor()
            cur.execute(sql, tk)
            conn.commit()
        conn.close()
    except Error as e:
        print(e)


# def checkWalletExists():





