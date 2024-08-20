#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request, url_for,flash, redirect
import requests
from . import db
import sys
import threading
from . import rabbitmq_publish
from . import rabbitmq_consume
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(test_config=None):
    
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    app.config.update(
        TESTING=False,
        SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',    
    )
    # Default configuration
    app.config['SERVER_NAME'] = 'potatomarket-0393ca13f662.herokuapp.com'
    app.config['APPLICATION_ROOT'] = '/src'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    
    # Override configuration if in testing mode
    if app.config['TESTING']:
        app.config['SERVER_NAME'] = '127.0.0.1:5000'
        app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    
    # Initialize the database and create the table on app start
    with app.app_context():
        db.init_db()
        db.populate_data()
    
    
    ################################### Potato Listings Marketplace - Main Code #######################################
    #  Index is the base listings page . it is populated by means of reading from a Rest API call ( presumably from country wide markets)
    #  Sellers page allows one to add a listing to the main page.
    #  From index page , we have a buy button that when clicked , places a hold on the listing and sends the listing id to a Rabbit MQ 
    #  The Rabbit MQ processes them for payment ( empty stub method ) and on consuming from queue marks the listing as sold
    #  on hold  and sold listings are displayed on the buyers page.
    #  Data Collection & Data Analysis routines are present at the bottom of the app.py file.
    ################################### Potato Listings Marketplace - Main Code #######################################
    @app.route('/index')
    def index():
        # Build the URL for the API endpoint dynamically
        api_url = url_for('api-listings', _external=True)
        print(api_url, file=sys.stderr)
        response = requests.get(api_url)
        listings_data = response.json()
        #print(listings_data, file=sys.stderr)
        return render_template('index.html', listings=listings_data)
    
    @app.route('/sellers')
    def sellers():
        return render_template('sellers.html')
    
    @app.route('/buyers')
    def buyers():
        api_url = url_for('api-listings-sold', _external=True)
        response = requests.get(api_url)
        listings_data = response.json()
        for i in listings_data:
            if i["Status"] == "onhold":
                print(i, file=sys.stderr)
                rabbitmq_consume.listing_consume_rabbitmq()
        return render_template('buyers.html', listings=listings_data)
    
    ################################### Potato Listings Marketplace - mock Rest API endpoints #######################################
    
    @app.route('/api/listings', endpoint="api-listings", methods=['GET'])
    def fetch_all():
        listings = db.fetch_all_unsold()
        return jsonify(listings)
    
    @app.route('/api/listings-sold', endpoint="api-listings-sold", methods=['GET'])
    def fetch_all():
        listings = db.fetch_all_sold()
        return jsonify(listings)
    
    
    
    ################################### Potato Listings Marketplace -methods for operations  #######################################
    
    ## Buy method moves the listing to on hold status and sends the listing id to a Rabbit MQ for completing payment ( stub)
    @app.route('/buy', methods=['POST'])
    def buy():
        item = request.json.get('item')
        print(item, file=sys.stderr)
        db.update_one_hold(item['Id'])
        rabbitmq_publish.listing_publish_rabbitmq(item['Id'])
        return jsonify({"message": f"Purchase reserved for {item['Id']}"})
    
    
    @app.route('/sold', methods=['POST'])
    def sold():
        item = request.json.get('item')
        db.update_one_sold(item['Id'])
        return jsonify({"message": f"Purchase completed for {item['Id']}"})
    
    @app.route('/api/populate_data', methods=['POST'])
    def populate_data():
        db.populate_data()
        return jsonify({"message": "Data populated successfully"}), 201
    
    @app.route('/listing/<int:id>', methods=['GET'])
    def fetch_one(id):
        listing = db.fetch_one(id)
        return jsonify(listing), 200
    
    @app.route('/listing/hold/<int:id>', methods=['PUT'])
    def update_one_hold(id):
        db.update_one_hold(id)
        return jsonify({"message": "Listing status updated to 'onhold'"}), 200
    
    @app.route('/listing/sold/<int:id>', methods=['PUT'])
    def update_sold(id):
        db.update_sold(id)
        return jsonify({"message": "Listing status updated to 'sold'"}), 200
    
    # Route to display the form and handle form submissions
    @app.route('/add-listing', methods=['GET', 'POST'])
    def add_listing():
        if request.method == 'POST':
            # Get form data
            type_choice = request.form.get('type')
            state_choice = request.form.get('state_of_origin')
            grade_choice = request.form.get('grade')
            weight_choice = request.form.get('weight')
            amount_choice = request.form.get('amount')
            status_choice='available'
            new_listing_id =db.insert_data(type_choice, state_choice, grade_choice, weight_choice, amount_choice, status_choice)
            # Flash a message with the ID for display
            print(new_listing_id, file=sys.stderr)
    
            return render_template('sellers.html',listingid=new_listing_id)
    
        # Render the form template
        return render_template('sellers.html')
    
    
    ########### Dummy methods to satisfy first assignment requirements - Receives input and displays the same. ####################
    @app.route("/")
    def main():
        return '''
         <form action="/echo_user_input" method="POST">
             <input name="user_input">
             <input type="submit" value="Submit!">
         </form>
         '''
    
    @app.route("/echo_user_input", methods=["POST"])
    def echo_input():
        input_text = request.form.get("user_input", "")
        return "You entered: " + input_text
    
    
    
    ############################ Production monitoring - keep alive indicator for health  ########################################
    @app.route("/health_check")
    def is_alive():
        return "I am healthy", 200
    
    
    ############################ Data Analysis ########################################
    from . import dataanalyzer
    analyzer = dataanalyzer.DataAnalyzer()
    
    @app.route('/state_report')
    def state_report():
        return analyzer.generate_state_report()
    
    @app.route('/grade_report')
    def grade_report():
        return analyzer.generate_grade_report()
    
    @app.route('/display_report')
    def display_report():
        return analyzer.display_report()
    
    ############################ Data Collection ########################################
    from . import datacollector
    # Initialize the DataCollector with the app context
    data_collector = datacollector.DataCollector(app)
    
    # Start the data collection in a background thread
    data_collection_thread = threading.Thread(target=data_collector.run, args=(10,), daemon=True)
    data_collection_thread.start()

    return app




