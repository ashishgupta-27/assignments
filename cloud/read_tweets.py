import json
from kafka import SimpleProducer, KafkaClient
import tweepy
import sys 

# Note: Some of the imports are external python libraries. They are installed on the current machine.
# If you are running multinode cluster, you have to make sure that these libraries
# and currect version of Python is installed on all the worker nodes.

topic=''

class TweeterStreamListener(tweepy.StreamListener):
    """ A class to read the twitter stream and push it to Kafka"""

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        client = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(client, async = True,
                          batch_send_every_n = 1000,
                          batch_send_every_t = 10)

    def on_status(self, status):
        """ This method is called whenever new data arrives from live stream.
        We asynchronously push this data to kafka queue"""
        msg =  status.text.encode('utf-8')
	print(msg)
        try:
            self.producer.send_messages(topic, msg)
        except Exception as e:
            print(e)
            return False
        return True

    def on_error(self, status_code):
	try:
		api.verify_credentials()
    		print("Authentication OK")
	except:
		print("Error during authentication")
        print("Error received in kafka producer. Status code is "+str(status_code))
        return True # Don't kill the stream

    def on_timeout(self):
        return True # Don't kill the stream

if __name__ == '__main__':

    consumer_key = '<CHANGE_VALUES_HERE>'
    consumer_secret = '<CHANGE_VALUES_HERE>'
    access_key = '<CHANGE_VALUES_HERE>'
    access_secret = '<CHANGE_VALUES_HERE>'

    topic=sys.argv[1]

    # Create Auth object
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # Create stream and bind the listener to it
    stream = tweepy.Stream(auth, listener = TweeterStreamListener(api))

    #Custom Filter rules pull all traffic for those filters in real time.
    #stream.filter(track = ['love', 'hate'], languages = ['en'])
    #stream.filter(locations=[-180,-90,180,90], languages = ['en'])

    if topic == 'NY':
    	stream.filter(locations=[-74,40,-73,41], languages = ['en']) #get tweets only of new york 
    elif topic == 'CA':
    	stream.filter(locations=[-122.75,36.8,-121.75,37.8], languages = ['en']) #get tweets of san francisco, california