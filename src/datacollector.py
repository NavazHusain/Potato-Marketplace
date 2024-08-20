import time
import threading
import requests
from flask import Flask, url_for, current_app as app,jsonify,request
import sys
import sqlite3
from . import db

DATABASE = 'listings.db'



class DataCollector:
    def __init__(self, app,db=DATABASE,fetch_uri='http://127.0.0.1:5000/api/listings'):
        self.app = app
        self.db = db
        self.fetch_uri=fetch_uri

    def get_data_listings_forsale(self):
        with self.app.app_context():
            api_url = self.fetch_uri
            try: 
                response = requests.get(api_url)
                data=response.json()
                return data
            except:
                pass
            listings = db.fetch_all_unsold()
            return listings

    def collect_data(self):
        with self.app.app_context():
            current_data = self.get_data_listings_forsale()
            for item in current_data:
                #print(item, file=sys.stderr)
                type_choice  = item['Type']
                state_choice  = item['State_of_Origin']
                grade_choice  = item['Grade']
                weight_choice  = item['Weight']
                amount_choice  = item['Amount']
                status_choice  = item['Status']
                try:
                    self.insert_data_dc(type_choice, state_choice, grade_choice, weight_choice, amount_choice, status_choice)
                except :
                    print(f"Skipping entry due to unique constraint violation:")

    ### Data Collection Subroutines.
    def insert_data_dc(self,type_choice, state_choice, grade_choice, weight_choice, amount_choice, status_choice):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
    
        c.execute('''
                INSERT OR IGNORE INTO datacollector_listings (Type, State_of_Origin, Grade, Weight, Amount, Status)
                VALUES (?, ?, ?, ?, ?, ?)  RETURNING Id
            ''', (type_choice, state_choice, grade_choice, weight_choice, amount_choice, status_choice))
        row = c.fetchone()
        (inserted_id, ) = row if row else None
        conn.commit()
        conn.close()
        return inserted_id


    def run(self, interval=300):
        while True:
            self.collect_data()
            time.sleep(interval)


