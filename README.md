# Potato-Marketplace

FINAL CAPSTONE PROJECT: POTATO MARKETPLACE 

TABLE OF CONTENTS
FinAl Capstone Project: Potato marketplace	1
Introduction :	1
High Level Architecture Diagram :	2
Detail Design Description:	2
Buyer workflow :	2
Seller Workflow :	3
Design Decisions:	4
System Requirements & Testing Strategies :	4
General Rubric A Level Work  & its mapping to features on the Potato Marketplace project	5


INTRODUCTION: 
To build a capstone project that satisfies the rubric given out at the beginning of this course, I have decided to build a sample marketplace application. By its very nature this sort of apps implements frontends, backends with databases, workflows that need an event collaboration messaging , reporting etc .
The proposed Potato marketplace provides a one stop solution to serve bulk potato buyers and sellers and act as an interface between them.  The entire project is hosted on 
https://potatomarket-0393ca13f662.herokuapp.com/index


HIGH LEVEL ARCHITECTURE DIAGRAM : 
 


DETAIL DESIGN DESCRIPTION: 

The application provides  simple , usable workflows for both buyers and sellers who will be the main users .
BUYER WORKFLOW : 
Step 1: 
Scan the listings fetched from Rest API call which brings data from countrywide to single portal on index page.  https://potatomarket-0393ca13f662.herokuapp.com/index
 
Step 2 :
 Click on buy which places a hold on the order ( will appear as greyed out with status 'onhold') and pushes the listings details to a Rabbit MQ even messaging system to handle  activities like payment and delivery . 
Step 3:  
Consumes messages from Rabbit MQ , verifies payment and changes the status of the listing from onhold to sold. 
Step 4: 
View the Buyers  page  to get details on the sale . Refresh the page if needed to get the message consumed from Rabbit MQ.
https://potatomarket-0393ca13f662.herokuapp.com/buyers

SELLER WORKFLOW :
Step 1 : 
Access the sellers webpage , provide necessary details and click submit . 
    Type : Russet, Gold, Idaho Red
   State of Origin : Nebraska, Michigan, Maine, Minnesota, Colorado, North Dakota, Oregon, Wisconsin, Idaho
   Grade  : Excellent , Good , Middling , Cattle Feed
   Weight : Random number between 10 and 1000
   Amount : Random number between 1 and 10
https://potatomarket-0393ca13f662.herokuapp.com/sellers

Step 2 :
 View the details of the listing on the index page.
Step 3: 
View the reports page  to get details on sales . 
 https://potatomarket-0393ca13f662.herokuapp.com/display_report

DESIGN DECISIONS: 
The entire stack is implemented as a Python Flask application. The database is Sqlite3  and the messaging system is Rabbit MQ. 
Justifications for design decisions:
Python Flask is a complete system development environment for all eventualities, including scaling up for performance, adding security considerations and other future growth . At the same time it is very basic and easy to start off with . This perfectly captures the need for the capstone project where the drive to show a working app with all fundamentals present – a minimum viable product ( MVP ) is important 
SQLite was chosen as the database due to its ease of usage. In general, for  a marketplace without geographical distribution, the general principle is to have its backend in RDBMS / SQL type of databases . This helps ensuring ACID , as well as removing the need for maintaining and configuring NOSQL databases .
RDBMS like Google’s Cloud Spanner are also available for geographically distributed apps, but in general we should implement NOSQL only if there is a specific application functional or nonfunctional requirement that calls for it . 


