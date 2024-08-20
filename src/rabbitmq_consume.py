import pika, os
import json
from . import db
import sys

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
#url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')

# going with a free plan on https://www.cloudamqp.com/ to implement the Event Colloboration messaging portion of the project . 
# Potato Marketplace Seqeunce of Operations 
# Listing is displayed on marketplace where data comes from an api call . 
# Sellers page to add new listing manually is available . 
# On the main page, clicking buy next to a listing places that listing on hold status ( updated in the DB and published to Rabbit MQ )
# This is the step implemnted here in def listing_publish_rabbitmq:
# We assume that an external process reads from the rabbit MQ and completes formalities like payment and dleivery which is outside our scope to code . 
# Another process will consume the entries from rabbit mq , once consumed the status of the listing is updated as sold and it disappears from our sales page.

def listing_consume_rabbitmq():
    url='amqps://fvfqljze:E989iAqauDa_E7uVrZdi3oV33ds2O0-F@shrimp.rmq.cloudamqp.com/fvfqljze'
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    connection = pika.BlockingConnection(
          pika.ConnectionParameters(
            heartbeat=50,
            blocked_connection_timeout=10,
            host='shrimp.rmq.cloudamqp.com',
            port=5672,
            virtual_host='fvfqljze',
            credentials=pika.PlainCredentials(
              username='fvfqljze',
              password='E989iAqauDa_E7uVrZdi3oV33ds2O0-F'
            )
          )
        )
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='PotatoListing') # Declare a queue
    
    
    #channel.basic_consume('PotatoListing',callback,auto_ack=True)
    
    channel.basic_qos(prefetch_count=1) # Ensure only one message is processed at a time
    
    method_frame, header_frame, body = channel.basic_get(queue='PotatoListing')
    
    if method_frame:
        on_message(channel, method_frame, header_frame, body)
    else:
        print("No messages in the queue.")

    print(' [*] Waiting for messages:')
    #channel.start_consuming()
    # Close the channel and the connection
    channel.close()
    connection.close()

def on_message(channel, method_frame, header_frame, body):
    print("Received message:", body)
    data=json.loads(body.decode('utf8'))
    print(data["id"], file=sys.stderr)
    db.update_one_sold(data["id"])
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    # Stop consuming after one message
    channel.stop_consuming()


#if __name__ == '__main__':
#    listing_consume_rabbitmq()