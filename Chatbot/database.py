import sqlite3
import json
from datetime import datetime

timeframe = '2015-05'
sql_transaction = []

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()


def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS parent_reply (parent_id TEXT PRIMARY KEY, comment_id TEST UNIQUE, parent TEXT, comment TEXT, subreddit TEXT, unix INT, score INT)")


def format_data(data):
    data = data.replace("\n", "  newlinechar  ").replace(
        "\r", "  retrunchar  ").replace('"', "'")
    return data


def find_existing_score(pid):
    try:
        sql = "SELECT score FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(
            pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception e:
        retutn False


def acceptable(data):
    if len(date.spit(' ')) > 50 or len(data) < 1:
        return False
    elif len(data) > 1000:
        return False
    elif data = '[deleted]' or data = '[removed]':
        return False
    else:
        return True


def parent_data(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(
            pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception e:
        retutn False


if __name__ == "__main__":
    create_table()
    row_counter = 0
    paired_rows = 0

    with open("/home/localhost/Project/PythonProjects/Chatbot/Data/{}/RC_{}".format(timeframe.split('-')[0], timeframe), buffering=1000) as f:
        for row in f:
            row_counter += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            created_utc = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']
            parent_data = find_parent(parent_id)

            if score >= 2:
                existing_comment_score = find_existing_score(parent_id)
                if existing_comment_score:
                    if score > existing_comment_score:
