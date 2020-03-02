#!/usr/bin/env python3
import os 
import datetime
import mysql.connector 
from dotenv import load_dotenv
load_dotenv()

ext_mydb = mysql.connector.connect(
  host=os.getenv("ext_hostname"),
  user=os.getenv("ext_username"),
  passwd=os.getenv("ext_password"),
  database=os.getenv("ext_db")
)
ext_cursor = ext_mydb.cursor()

mydb = mysql.connector.connect(
  host=os.getenv("hostname"),
  user=os.getenv("username"),
  passwd=os.getenv("password"),
  database=os.getenv("db")
)
cursor = mydb.cursor()

def update_local_db(days_since=1):
    print("Importing swaps")
    ext_cursor.execute("SELECT * FROM swaps WHERE started_at >= now() - INTERVAL "+str(days_since)+" DAY ORDER BY started_at;")
    ext_result = ext_cursor.fetchall()
    for x in ext_result:
        try:
            sql = "INSERT INTO dexstatsDB.swaps VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, x)
            mydb.commit()
            print(x)
            print(cursor.rowcount, "record inserted.")
        except Exception as e:
            print(e)

    print("\nImporting failed swaps")
    ext_cursor.execute("SELECT * FROM swaps_failed WHERE started_at >= now() - INTERVAL "+str(days_since)+" DAY ORDER BY started_at; ")
    ext_result = ext_cursor.fetchall()
    for x in ext_result:
        try:
            sql = "INSERT INTO dexstatsDB.swaps_failed VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, x)
            mydb.commit()
            print(x)
            print(cursor.rowcount, "record inserted.")
        except Exception as e:
            print(e)

def count_rows(db, col='UUID', days_since=1):
    sql = "SELECT COUNT("+col+") FROM "+db+" WHERE started_at >= now() - INTERVAL "+str(days_since)+" DAY ORDER BY started_at;"
    ext_cursor.execute(sql)
    ext_result = ext_cursor.fetchone()
    print(ext_result)
    return ext_result

success = count_rows('swaps', 'UUID', 1)
failed = count_rows('swaps_failed', 'UUID', 1)

print("SUCCESS: "+str(success[0]))
print("FAILED: "+str(failed[0]))

def get_failed(maker_coin, taker_coin, mins_since):
    sql = "SELECT * FROM swaps_failed"
    conditions = [] 
    if taker_coin:
        conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        conditions.append("maker_coin = '"+maker_coin+"'")
    if mins_since:
        conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    ext_cursor.execute(sql)
    ext_result = ext_cursor.fetchall()
    print(ext_result)
    return ext_result


def get_success(maker_coin, taker_coin, mins_since):
    sql = "SELECT * FROM swaps"
    conditions = []
    if taker_coin:
        conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        conditions.append("maker_coin = '"+maker_coin+"'")
    if mins_since:
        conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    ext_cursor.execute(sql)
    ext_result = ext_cursor.fetchall()
    print(ext_result)
    return ext_result
