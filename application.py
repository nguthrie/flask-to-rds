from flask import Flask, request

import random
import pymysql
import time
import json
import os


application = app = Flask(__name__)

database = os.environ.get("RDS_HOSTNAME")
username = os.environ.get("RDS_USERNAME")
password = os.environ.get("RDS_PASSWORD")


db = pymysql.connect(database, username, password, autocommit=True)


@app.route('/environment_variables', methods=["GET"])
def environment_variables():

    database = os.environ.get("RDS_HOSTNAME")
    username = os.environ.get("RDS_USERNAME")
    password = os.environ.get("RDS_PASSWORD")

    return json.dumps({"database": database, "username": username, "password": password})

@app.route('/show_databases', methods=["GET"])
def show_databases():

    cursor = db.cursor()

    sql = '''show databases;'''
    cursor.execute(sql)
    databases = {}
    for index, database in enumerate(cursor):
        databases[index] = database[0]

    cursor.close()

    return json.dumps(databases)


@app.route("/show_process_list", methods=["GET"])
def show_process_list():
    cursor = db.cursor()

    sql = '''SHOW PROCESSLIST'''
    cursor.execute(sql)
    response_dict = {}
    for index, row in enumerate(cursor):
        response_dict[index] = row

    cursor.close()
    return json.dumps(response_dict)


def create_project_database():
    cursor = db.cursor()
    sql = '''CREATE DATABASE IF NOT EXISTS main_app_database;'''
    cursor.execute(sql)
    cursor.close()


@app.route('/select_database', methods=["GET"])
def use_database():
    cursor = db.cursor()
    sql = '''USE main_app_database;'''
    cursor.execute(sql)
    cursor.close()
    return "Selected main_app_database (hard-coded)."

def drop_database():
    cursor = db.cursor()
    sql = '''DROP DATABASE IF EXISTS main_app_database;'''
    cursor.execute(sql)
    cursor.close()

def create_test_table():

    cursor = db.cursor()

    sql = '''CREATE TABLE IF NOT EXISTS main_test_table (c1_index INT PRIMARY KEY);'''
    cursor.execute(sql)
    cursor.close()

@app.route('/create_table_post', methods=["POST"])
def create_test_table_POST():
    cursor = db.cursor()
    incoming_json = request.get_json()
    print(incoming_json)
    if incoming_json:
        name = incoming_json['name']
    else:
        return "Need to pass valid JSON with table name."
    sql = '''CREATE TABLE IF NOT EXISTS {} (c1_index INT PRIMARY KEY);'''.format(name)
    cursor.execute(sql)
    cursor.close()
    return show_tables()

@app.route("/show_tables", methods=["GET"])
def show_tables():
    cursor = db.cursor()

    sql = '''SHOW TABLES;'''
    cursor.execute(sql)
    table_dict = {}
    for index, table in enumerate(cursor):
        table_dict[index] = table[0]
    cursor.close()
    return json.dumps(table_dict)


def select_all_data_in_table():
    cursor = db.cursor()
    sql = '''SELECT *
    FROM main_test_table;'''
    cursor.execute(sql)
    rows = []
    for row in cursor:
        rows.append(row)
    cursor.close()
    return rows


def drop_table():
    cursor = db.cursor()
    sql = '''DROP TABLE IF EXISTS main_test_table;'''
    cursor.execute(sql)
    cursor.close()

@app.route('/')
def home():
    return "Hello"


@app.route('/setup', methods=['GET'])
def setup():
    """Clears and sets up database. Can toggle drop_database for persistence."""
    show_databases()
    drop_database()
    create_project_database()
    use_database()
    # drop_table()
    create_test_table()
    return show_tables()


int_list = []
@app.route('/insert_random_number', methods=["POST"])
def insert_random_value():
    """Adds individual numbers - index must be passed in POST request
    Adds a random number between 0 and 20, avoids duplicates and restarts when 10 numbers have been added."""

    cursor = db.cursor()

    # once the list has 10 elements, reset the database
    global int_list
    select_all_json = select_all_to_json()
    if len(json.loads(select_all_json)) == 10:
        setup()
        int_list = []

    # add elements with duplicate protection
    rand_int = random.randint(1, 20)
    if not (rand_int in int_list):
        int_list.append(rand_int)
        command = '''INSERT INTO main_test_table (c1_index) values ({})'''.format(rand_int)
        sql = command
        cursor.execute(sql)
        cursor.close()
        return select_all_to_json()
    else:
        cursor.close()
        return "Duplicate avoided"



@app.route('/insert_random_number_repeat', methods=["POST"])
def insert_random_value_repeat():
    """Add enteries number of parameters with time delay delay, then show table."""
    cursor = db.cursor()
    incoming_json = request.get_json()
    entries = incoming_json['entries']
    delay = incoming_json['delay']
    index = 1
    while index <= entries:
        time.sleep(delay)
        rand_int = random.randint(1, 10)
        command = '''INSERT INTO main_test_table (c1_index) values ({})'''.format(rand_int)
        sql = command
        cursor.execute(sql)
        index += 1

    db.commit()
    cursor.close()
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

    # app.run(host='127.0.0.1', port=5001, debug=True)
    app.run(host='0.0.0.0', port=80)

