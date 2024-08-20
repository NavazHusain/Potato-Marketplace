import requests
from flask import Flask, url_for, current_app as app,jsonify,render_template
import sqlite3
from random import choice, randint
import sys

DATABASE = 'listings.db'

class DataAnalyzer:
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    ##Data Analysis Subroutines
    def fetch_report_state(self,state):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT State_of_Origin, sum(Weight) as weight, sum(Amount) as amount FROM datacollector_listings where State_of_Origin = ? group by State_of_Origin''' , (state,))
        row = c.fetchone()
        conn.close()
        return dict(zip([column[0] for column in c.description], row)) if row else None
    
    def fetch_report_grade(self,grade):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT Grade, sum(Weight) as weight, sum(Amount) as amount FROM datacollector_listings where  Grade = ? group by Grade''' , (grade,))
        row = c.fetchone()
        conn.close()
        return dict(zip([column[0] for column in c.description], row)) if row else None
    
    def fetch_all_state(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT State_of_Origin FROM datacollector_listings  group by State_of_Origin''' )
        rows = c.fetchall()
        conn.close()
        return [row[0] for row in rows] if rows else []
    
    def fetch_all_grade(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT Grade FROM datacollector_listings  group by grade''' )
        rows = c.fetchall()
        conn.close()
        return [row[0] for row in rows] if rows else []
    
    def generate_state_report(self):
            states = self.fetch_all_state()
            report = []
            for state in states:
                report.append(self.fetch_report_state(state))
            return jsonify(report)
    
    def generate_grade_report(self):
        grades = self.fetch_all_grade()
        report = []
        for grade in grades:
            report.append(self.fetch_report_grade(grade))
        return jsonify(report)
    def display_report(self):
        state_report = self.generate_state_report().json
        grade_report = self.generate_grade_report().json
        return render_template('report.html', state_report=state_report, grade_report=grade_report)