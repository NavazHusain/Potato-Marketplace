import sqlite3
from random import choice, randint
import sys

DATABASE = 'listings.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Type TEXT,
            State_of_Origin TEXT,
            Grade TEXT,
            Weight TEXT,
            Amount TEXT,
            Status TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS datacollector_listings (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Type TEXT,
            State_of_Origin TEXT,
            Grade TEXT,
            Weight TEXT,
            Amount TEXT,
            Status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def populate_data():
    types = ["Russet", "Gold", "Idaho Red"]
    states = ["Nebraska", "Michigan", "Maine", "Minnesota", "Colorado", "North Dakota", "Oregon", "Wisconsin", "Idaho"]
    grades = ["Excellent", "Good", "Middling", "Cattle Feed"]

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('delete from listings')
    for _ in range(50):
        type_choice = choice(types)
        state_choice = choice(states)
        grade_choice = choice(grades)
        weight_choice = str(randint(10, 1000))
        amount_choice = str(randint(1, 10))
        status_choice = "available"

        c.execute('''
            INSERT INTO listings (Type, State_of_Origin, Grade, Weight, Amount, Status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (type_choice, state_choice, grade_choice, weight_choice, amount_choice, status_choice))

    conn.commit()
    conn.close()


def insert_data(type_choice, state_choice, grade_choice, weight_choice, amount_choice, status_choice):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
            INSERT INTO listings (Type, State_of_Origin, Grade, Weight, Amount, Status)
            VALUES (?, ?, ?, ?, ?, ?)  RETURNING Id
        ''', (type_choice, state_choice, grade_choice, weight_choice, amount_choice, status_choice))
    row = c.fetchone()
    (inserted_id, ) = row if row else None
    conn.commit()
    conn.close()
    return inserted_id




def fetch_all_unsold():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT Id,Type, State_of_Origin, Grade, Weight, Amount, Status FROM listings WHERE Status in ( "available","onhold") order by Id desc
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(zip([column[0] for column in c.description], row)) for row in rows]

def fetch_all_sold():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT Id,Type, State_of_Origin, Grade, Weight, Amount, Status FROM listings WHERE Status in ("onhold", "sold") order by Id desc
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(zip([column[0] for column in c.description], row)) for row in rows]

def fetch_one(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT Id,Type, State_of_Origin, Grade, Weight, Amount, Status FROM listings WHERE Id = ?
    ''', (id,))
    row = c.fetchone()
    conn.close()
    return dict(zip([column[0] for column in c.description], row)) if row else None

def update_one_hold(id):
    conn = sqlite3.connect(DATABASE)
    print(id, file=sys.stderr)
    c = conn.cursor()
    c.execute('''
        UPDATE listings SET Status = "onhold" WHERE Id = ?
    ''', (id,))
    conn.commit()
    conn.close()

def update_one_sold(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        UPDATE listings SET Status = "sold" WHERE Id = ?
    ''', (id,))
    conn.commit()
    conn.close()

