import unittest
import os
import sqlite3
from flask import Flask, jsonify, render_template_string
from src import datacollector, dataanalyzer  # Replace with the actual module name
from unittest.mock import patch, MagicMock
import tempfile

class TestDataIntegration(unittest.TestCase):
    
    def setUp(self):
        # Set up a Flask app context for testing
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

        # Set up an in-memory SQLite database for testing
        self.db, self.db_path = tempfile.mkstemp(suffix='.sqlite')
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS datacollector_listings (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Type TEXT,
                    State_of_Origin TEXT,
                    Grade TEXT,
                    Weight INTEGER,
                    Amount INTEGER,
                    Status TEXT
                )
            ''')
            conn.commit()
        
        # Initialize DataCollector and DataAnalyzer with the test database
        self.collector = datacollector.DataCollector(self.app, db=self.db_path, fetch_uri='/mock/api/listings')
        self.analyzer = dataanalyzer.DataAnalyzer(db_path=self.db_path)
        
        # Mock API response
        self.mock_api_data = [
            {"Type": "Gold", "State_of_Origin": "NY", "Grade": "A", "Weight": 100, "Amount": 1000, "Status": "For Sale"},
            {"Type": "Russet", "State_of_Origin": "CA", "Grade": "B", "Weight": 200, "Amount": 1500, "Status": "For Sale"},
        ]
        

    @patch('requests.get')
    def test_data_collection_and_analysis(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_api_data
        mock_get.return_value = mock_response
        
        # Collect data using the DataCollector
        with self.app.app_context():
            self.collector.collect_data()

        # Analyze the collected data using DataAnalyzer
        with self.app.app_context():
            # Test fetching report by state
            ny_report = self.analyzer.fetch_report_state("NY")
            self.assertEqual(ny_report['State_of_Origin'], "NY")
            self.assertEqual(ny_report['weight'], 100)
            self.assertEqual(ny_report['amount'], 1000)

            # Test fetching report by grade
            grade_a_report = self.analyzer.fetch_report_grade("A")
            self.assertEqual(grade_a_report['Grade'], "A")
            self.assertEqual(grade_a_report['weight'], 100)
            self.assertEqual(grade_a_report['amount'], 1000)
            
            # Test generating full report
            state_report = self.analyzer.generate_state_report().json
            self.assertEqual(len(state_report), 2)  # Two states in the mock data

            grade_report = self.analyzer.generate_grade_report().json
            self.assertEqual(len(grade_report), 2)  # Two grades in the mock data
            

    def tearDown(self):
        # Cleanup actions if needed (e.g., closing database connections)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

if __name__ == '__main__':
    unittest.main()
