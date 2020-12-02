from flask import Flask, render_template, request

import random
import pymysql
import time
import json

import credentials


application = app = Flask(__name__)

db = pymysql.connect(credentials.database, credentials.user,
                     credentials.password, local_infile=True)
cursor = db.cursor()


def show_databases():
    sql = '''show databases;'''
    cursor.execute(sql)
    for databases in cursor:
        print(databases[0])


def create_project_database():
    sql = '''CREATE DATABASE IF NOT EXISTS main_app_database;'''
    cursor.execute(sql)


def use_database():
    sql = '''USE main_app_database;'''
    cursor.execute(sql)


def drop_database():
    sql = '''DROP DATABASE IF EXISTS main_app_database;'''
    cursor.execute(sql)


def create_test_table():
    sql = '''CREATE TABLE IF NOT EXISTS main_test_table (c1_index INT PRIMARY KEY, c2_random_int INT);'''
    cursor.execute(sql)


def show_tables():
    sql = '''SHOW TABLES;'''
    cursor.execute(sql)
    table_list = []
    for table in cursor:
        table_list.append(table[0])
    return table_list


def select_all_data_in_table():
    sql = '''SELECT *
    FROM main_test_table;'''
    cursor.execute(sql)
    rows = []
    for row in cursor:
        rows.append(row)
    return rows

def drop_table():
    sql = '''DROP TABLE IF EXISTS main_test_table;'''
    cursor.execute(sql)


@app.route('/')
def home():
    return "Hello"


@app.route('/setup', methods=['GET'])
def setup():
    """Clears and sets up database. Can toggle drop_database for persistence."""
    show_databases()
    # drop_database()
    create_project_database()
    use_database()
    # drop_table()
    create_test_table()
    tables_list = show_tables()
    return "Tables: {}".format(tables_list[0])


@app.route('/insert_random_number', methods=["POST"])
def insert_random_value():
    """Adds individual numbers - index must be passed in POST request"""
    incoming_json = request.get_json()
    index = incoming_json['index']
    rand_int = random.randint(1, 10)
    command = '''INSERT INTO main_test_table (c1_index, c2_random_int) values ({}, {})'''.format(index, rand_int)
    sql = command
    cursor.execute(sql)
    return select_all_to_json()

@app.route('/insert_random_number_repeat', methods=["POST"])
def insert_random_value_repeat():
    """Add enteries number of parameters with time delay delay, then show table."""
    incoming_json = request.get_json()
    entries = incoming_json['entries']
    delay = incoming_json['delay']
    index = 1
    while index <= entries:
        time.sleep(delay)
        rand_int = random.randint(1, 10)
        command = '''INSERT INTO main_test_table (c1_index, c2_random_int) values ({}, {})'''.format(index, rand_int)
        sql = command
        cursor.execute(sql)
        index += 1

    return select_all_to_json()


@app.route('/select_all', methods=['GET'])
def select_all_to_json():
    """Return rows of table as JSON"""
    i = 1
    rows = select_all_data_in_table()
    row_dict = {}
    for row in rows:
        row_dict[i] = row
        i += 1
    return json.dumps(row_dict)


if __name__ == "__main__":

    # app.run(host='127.0.0.1', port=5000, debug=True)
    app.run(host='0.0.0.0', port=80, debug=True)

