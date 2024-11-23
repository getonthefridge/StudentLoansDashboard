from os import environ as env
from decimal import Decimal

import mysql.connector


def connection():
    try:
        db = mysql.connector.connect(
            host=env['DB_HOST'],
            user=env['DB_USER'],
            passwd=env['DB_PASS'],
            database=env['DATABASE']
        )
        """
        DB_HOST=localhost;
        DB_PASS=12345678;
        DB_USER=root;
        DATABASE=StudentLoans
        """

        return db
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database:\n{err}")
        return None


def selectIncome(conn):
    db = conn.cursor()
    db.execute('SELECT * FROM Income')
    return db.fetchall()


def selectExpenses(conn):
    db = conn.cursor()
    db.execute('SELECT * FROM Expenses;')
    return db.fetchall()


def incomeTotal(conn):
    db = conn.cursor()
    db.execute('SELECT SUM(Amount) FROM Income;')
    results = db.fetchall()
    results = results[0][0].quantize(Decimal('0.00'))
    return results


def expenseTotal(conn):
    db = conn.cursor()
    db.execute('SELECT SUM(Amount) FROM Expenses;')
    results = db.fetchall()
    results = results[0][0].quantize(Decimal('0.00'))
    return results


def addRow(conn, table, date, details, amount):
    db = conn.cursor()
    query = f"""INSERT INTO {table} (Date, Details, Amount) 
                        VALUES (%s,
                                %s,
                                %s)"""
    values = (date, details, amount)
    db.execute(query, values)
    conn.commit()



def deleteRow(conn, table, id):
    db = conn.cursor()
    query = f"""DELETE FROM {table} WHERE ID = {id}"""
    db.execute(query)
    conn.commit()


def editRow(conn, table, id, date, details, amount):
    db = conn.cursor()
    query = f"""
        UPDATE {table} 
        SET Date = %s,
            Details = %s,
            Amount = %s
        WHERE ID = %s
    """
    values = (date, details, str(amount), id)
    db.execute(query, values)
    conn.commit()
