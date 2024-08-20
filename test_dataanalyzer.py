import unittest
import tempfile
import os
import sqlite3
from flask import Flask
from src import dataanalyzer  # Adjust the import according to your directory structure

class DataAnalyzerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()  # Push the app context
        
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.sqlite')
        
        # Create a new instance of the DataAnalyzer class with the temporary database path
        self.analyzer = dataanalyzer.DataAnalyzer(db_path=self.db_path)

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

            # Insert sample data for testing
            c.execute(
                "INSERT INTO datacollector_listings (State_of_Origin, Grade, Weight, Amount) VALUES ('Minnesota', 'Excellent', 200, 10)"
            )
            c.execute(
                "INSERT INTO datacollector_listings (State_of_Origin, Grade, Weight, Amount) VALUES ('Idaho', 'Good', 150, 15)"
            )
            conn.commit()

        # Initialize the test client
        self.client = self.app.test_client()

    def tearDown(self):
        # Close and remove the temporary database file
        os.close(self.db_fd)
        os.unlink(self.db_path)
        self.app_context.pop()  # Pop the app context to clean up


    def tearDown(self):
        # Close and remove the temporary database file
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_generate_state_report(self):
        state_report = self.analyzer.generate_state_report().json
        self.assertEqual(len(state_report), 2)
        self.assertIn('Minnesota', [state['State_of_Origin'] for state in state_report])

    def test_generate_grade_report(self):
        grade_report = self.analyzer.generate_grade_report().json
        self.assertEqual(len(grade_report), 2)
        self.assertIn('Excellent', [grade['Grade'] for grade in grade_report])



if __name__ == '__main__':
    unittest.main()