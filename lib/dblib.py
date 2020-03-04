#!/usr/bin/env python3
import os 
import datetime
import mysql.connector 
from dotenv import load_dotenv
import logging
import logging.handlers

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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

global unique_success_vals
global unique_fail_vals
unique_success_vals = {}
unique_fail_vals = {}
def update_local_db(days_since=1):
    print("Importing swaps")
    new_success = 0
    ext_cursor.execute("SELECT * FROM swaps WHERE started_at >= now() - INTERVAL "+str(days_since)+" DAY ORDER BY started_at;")
    result = ext_cursor.fetchall()
    for x in result:
        try:
            sql = "INSERT INTO dexstatsDB.swaps VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, x)
            mydb.commit()
            new_success += 1
        except Exception as e:
            print(e)
    logger.info(str(new_success)+" new successful swaps added to DB")

    print("\nImporting failed swaps")
    new_failed = 0
    ext_cursor.execute("SELECT * FROM swaps_failed WHERE started_at >= now() - INTERVAL "+str(days_since)+" DAY ORDER BY started_at; ")
    result = ext_cursor.fetchall()
    for x in result:
        try:
            sql = "INSERT INTO dexstatsDB.swaps_failed VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, x)
            mydb.commit()
            new_failed += 1
        except Exception as e:
            print(e)
    logger.info(str(new_failed)+" new failed swaps added to DB")
    success_cols = ['taker_coin', 'maker_coin', 'taker_gui', 'maker_gui', 'taker_version', 'maker_version']
    for col in success_cols:
        unique_success_vals[col] = get_unique_values('swaps', col)
    fail_cols = ['taker_coin', 'maker_coin', 'taker_gui', 'maker_gui', 'taker_version', 'maker_version', 'taker_error_type', 'maker_error_type']
    for col in fail_cols:
        unique_fail_vals[col] = get_unique_values('swaps_failed', col)

def get_unique_filter_values(table):
    if table == 'swaps':
        return unique_success_vals
    elif table == 'swaps_failed':
        return unique_fail_vals


def get_unique_values(table='swaps', col='taker_coin', mins_since=None):
    val_list = []
    sql = "SELECT DISTINCT "+col+" FROM "+table
    conditions = []
    conditions.append(col+" IS NOT NULL")
    if mins_since:
        conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    cursor.execute(sql)
    result = cursor.fetchall()
    for x in result:
        val_list.append(str(x[0]))
    return val_list

def count_rows(table='swaps', col='UUID', mins_since=None):
    conditions = []
    sql = "SELECT COUNT("+col+") FROM "+table
    if mins_since:
        conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

def get_failed(maker_coin=None, taker_coin=None, maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, taker_error_type: str=None, maker_error_type: str=None, mins_since=None):
    json_obj = "JSON_OBJECT( \
        'uuid', uuid, \
        'started_at', started_at, \
        'taker_coin', taker_coin, \
        'taker_amount', taker_amount, \
        'taker_error_type', taker_error_type, \
        'taker_error_msg', taker_error_msg, \
        'taker_gui', taker_gui, \
        'taker_version', taker_version, \
        'taker_pubkey', taker_pubkey, \
        'maker_coin', maker_coin, \
        'maker_amount', maker_amount, \
        'maker_error_type', maker_error_type, \
        'maker_error_msg', maker_error_msg, \
        'maker_gui', maker_gui, \
        'maker_version', maker_version, \
        'maker_pubkey', maker_pubkey \
        )"
    sql = "SELECT "+json_obj+" FROM swaps_failed"
    conditions = [] 
    if taker_coin:
        if taker_coin != "--ALL--":
            conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        if maker_coin != "--ALL--":
            conditions.append("maker_coin = '"+maker_coin+"'")
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_error_type:
        if maker_error_type != "--ALL--":
            conditions.append("maker_error_type = '"+maker_error_type+"'")
    if taker_error_type:
        if taker_error_type != "--ALL--":
            conditions.append("taker_error_type = '"+taker_error_type+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_success(maker_coin=None, taker_coin=None, maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, mins_since=None):
    json_obj = "JSON_OBJECT( \
        'uuid', uuid, \
        'started_at', started_at, \
        'taker_coin', taker_coin, \
        'taker_amount', taker_amount, \
        'taker_gui', taker_gui, \
        'taker_version', taker_version, \
        'taker_pubkey', taker_pubkey, \
        'maker_coin', maker_coin, \
        'maker_amount', maker_amount, \
        'maker_gui', maker_gui, \
        'maker_version', maker_version, \
        'maker_pubkey', maker_pubkey \
        )"
    sql = "SELECT "+json_obj+" FROM swaps"
    conditions = []
    if taker_coin:
        if taker_coin != "--ALL--":
            conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        if maker_coin != "--ALL--":
            conditions.append("maker_coin = '"+maker_coin+"'")
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_failed_count(group_by, maker_coin=None, taker_coin=None, maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, taker_error_type: str=None, maker_error_type: str=None, mins_since=None):
    if group_by == '--ALL--':
        group_by == 'uuid'
    json_obj = "JSON_OBJECT( \
            "+group_by+", COUNT("+group_by+") \
        )"
    sql = "SELECT "+json_obj+" FROM swaps_failed"
    conditions = [] 
    conditions.append(group_by+" IS NOT NULL")
    if taker_coin:
        if taker_coin != "--ALL--":
            conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        if maker_coin != "--ALL--":
            conditions.append("maker_coin = '"+maker_coin+"'")
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_error_type:
        if maker_error_type != "--ALL--":
            conditions.append("maker_error_type = '"+maker_error_type+"'")
    if taker_error_type:
        if taker_error_type != "--ALL--":
            conditions.append("taker_error_type = '"+taker_error_type+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    sql += " GROUP BY "+group_by
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_success_count(group_by, maker_coin=None, taker_coin=None, maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, mins_since=None):
    if group_by == '--ALL--':
        group_by == 'uuid'
    json_obj = "JSON_OBJECT( \
            "+group_by+", COUNT("+group_by+") \
        )"
    sql = "SELECT "+json_obj+" FROM swaps"
    conditions = []
    conditions.append(group_by+" IS NOT NULL")
    if taker_coin:
        if taker_coin != "--ALL--":
            conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        if maker_coin != "--ALL--":
            conditions.append("maker_coin = '"+maker_coin+"'")
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    sql += " GROUP BY "+group_by
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_taker_volume(maker_coin=None, taker_coin=None, maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, mins_since=None):
    json_obj = "JSON_OBJECT('coin', taker_coin, 'volume', SUM(taker_amount))"
    sql = "SELECT "+json_obj+" FROM swaps"
    conditions = []
    if taker_coin:
        if taker_coin != "--ALL--":
            conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        if maker_coin != "--ALL--":
            conditions.append("maker_coin = '"+maker_coin+"'")
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    sql += " GROUP BY taker_coin"
    sql += " ORDER BY taker_coin"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_maker_volume(maker_coin=None, taker_coin=None, maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, mins_since=None):
    json_obj = "JSON_OBJECT('coin', maker_coin, 'volume', SUM(maker_amount))"
    sql = "SELECT "+json_obj+" FROM swaps"
    conditions = []
    if taker_coin:
        if taker_coin != "--ALL--":
            conditions.append("taker_coin = '"+taker_coin+"'")
    if maker_coin:
        if maker_coin != "--ALL--":
            conditions.append("maker_coin = '"+maker_coin+"'")
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    sql += " GROUP BY maker_coin"
    sql += " ORDER BY maker_coin"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_mean_maker_price_KMD(maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, mins_since=None):
    json_obj = "JSON_OBJECT('maker_coin', maker_coin, 'taker_coin', taker_coin, \
                            'maker_amount', SUM(taker_amount), 'taker_amount', SUM(maker_amount), \
                            'KMD_price',  SUM(taker_amount)/SUM(maker_amount) \
                            )"
    sql = "SELECT "+json_obj+" FROM swaps"
    conditions = ["taker_coin = 'KMD'"]
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    sql += " GROUP BY maker_coin"
    sql += " ORDER BY maker_coin"
    cursor.execute(sql)
    result = cursor.fetchall()

    return result

def get_mean_taker_price_KMD(maker_gui=None, taker_gui=None, maker_version=None, taker_version=None,
                             maker_pubkey=None, taker_pubkey=None, mins_since=None):
    json_obj = "JSON_OBJECT('maker_coin', maker_coin, 'taker_coin', taker_coin, \
                            'maker_amount', SUM(taker_amount), 'taker_amount', SUM(maker_amount), \
                            'KMD_price',  SUM(maker_amount)/SUM(taker_amount) \
                            )"
    sql = "SELECT "+json_obj+" FROM swaps"
    conditions = ["maker_coin = 'KMD'"]
    if taker_gui:
        if taker_gui != "--ALL--":
            conditions.append("taker_gui = '"+taker_gui+"'")
    if maker_gui:
        if maker_gui != "--ALL--":
            conditions.append("maker_gui = '"+maker_gui+"'")
    if taker_version:
        if taker_version != "--ALL--":
            conditions.append("taker_version = '"+taker_version+"'")
    if maker_version:
        if maker_version != "--ALL--":
            conditions.append("maker_version = '"+maker_version+"'")
    if taker_pubkey:
        if taker_pubkey != "--ALL--":
            conditions.append("taker_pubkey = '"+taker_pubkey+"'")
    if mins_since:
        if mins_since != "--ALL--":
            conditions.append("started_at >= now() - INTERVAL "+str(mins_since)+" MINUTE")
    if len(conditions) > 0:
        condition = " WHERE "+" AND ".join(conditions)
        sql += condition
    sql += " GROUP BY taker_coin"
    sql += " ORDER BY taker_coin"
    cursor.execute(sql)
    result = cursor.fetchall()

    return result

update_local_db()
print(unique_success_vals.keys())
print(unique_fail_vals.keys())