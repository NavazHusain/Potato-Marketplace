import pika, os,json

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

def listing_publish_rabbitmq(id):
    url='amqps://fvfqljze:E989iAqauDa_E7uVrZdi3oV33ds2O0-F@shrimp.rmq.cloudamqp.com/fvfqljze'
    credentials = pika.PlainCredentials('fvfqljze', 'E989iAqauDa_E7uVrZdi3oV33ds2O0-F')
    parameters = pika.ConnectionParameters('shrimp.rmq.cloudamqp.com',
                                   5672,
                                   'fvfqljze',
                                   credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='PotatoListing') # Declare a queue
    message=json.dumps({ "id": id,  "message": "potato listing" })
    channel.basic_publish(exchange='',
                          routing_key='PotatoListing',
                          body=message)
    
    print(" [x] Sent ", id)
    connection.close()


#if __name__ == '__main__':
#    listing_publish_rabbitmq(500)