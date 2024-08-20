import unittest
from unittest.mock import patch, MagicMock
import tempfile
from flask import Flask
import sqlite3
import time
from src import datacollector

class TestDataCollector(unittest.TestCase):
    
    def setUp(self):
        # Set up a Flask app context for testing
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()  # Push the app context
        
        
        # Create a temporary database file
        self.db, self.db_path = tempfile.mkstemp(suffix='.sqlite')
        self.collector = datacollector.DataCollector(self.app,db=self.db_path)
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
        
    
    @patch('requests.get')
    def test_get_data_listings_forsale(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"Id": 1, "State_of_Origin": "Minnesota", "Grade": "Good", "Weight": 100, "Amount": 1000, "Status": "For Sale"}
        ]
        mock_get.return_value = mock_response
        with self.app.app_context():
            data = self.collector.get_data_listings_forsale()
            self.assertEqual(data[0]['Id'], 1)
            self.assertEqual(data[0]['State_of_Origin'], "Minnesota")
            self.assertEqual(data[0]['Grade'], "Good")
    
    def test_insert_data_dc(self):
        with self.app.app_context():
            inserted_id = self.collector.insert_data_dc( "Russet","Minnesota","Good", 100, 1000, "available") 
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
             SELECT  State_of_Origin FROM datacollector_listings WHERE Id = ?
            ''', (inserted_id,))
            row = c.fetchone()     
            self.assertEqual(row[0], 'Minnesota')


if __name__ == '__main__':
    unittest.main()
