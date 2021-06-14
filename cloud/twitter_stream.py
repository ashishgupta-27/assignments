from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import StorageLevel
from pyspark.mllib.fpm import FPGrowth
import operator
import numpy as np
import sys
#import matplotlib.pyplot as plt


def main():
    conf = SparkConf().setMaster("local[2]").setAppName("Streamer")
    sc = SparkContext(conf=conf)

    topic=sys.argv[1]

    # Creating a streaming context with batch interval of 10 sec
    ssc = StreamingContext(sc, 30)
    ssc.checkpoint("checkpoint")
    sc.setLogLevel("ERROR")
    kstream = KafkaUtils.createDirectStream(
    ssc, topics = [topic], kafkaParams = {"metadata.broker.list": 'localhost:9092'})
    
    tweets = kstream.map(lambda x: x[1].encode("ascii", "ignore"))
    tweets.persist(StorageLevel.MEMORY_AND_DISK)
    tweets.saveAsTextFiles('/home/cs19m012/tweets','.txt');
   
    tweets.pprint()
    tweets.count().map(lambda x:'Tweets in this batch: %s' % x).pprint()
    tweets_to_count = tweets.map(lambda x: ('count', 1))
    tweets.countByWindow(10*60,30).map(lambda x:'Total tweets till now: %s' % x).pprint()
    total_count = tweets_to_count.reduceByKeyAndWindow(lambda c1, c2: c1 + c2, None, 10*60, 30)
    #total_count.map(lambda (x,y) : Total tweets till now: %s' % y).pprint();

    #f=open('/home/cs19m012/count.txt', 'w')
    #f.write(str(total_count.collect()))
    #transactions = tweets.map(lambda line: line.strip().split(' '))
    #words = tweets.flatMap(lambda line:line.split(" "))
    #words.pprint()
    #model = FPGrowth.train(words, minSupport=0.1, numPartitions=2)
    #result = model.freqItemsets().collect()
    #for fi in result:
    #    print(fi)
    
    # Start the computation
    ssc.start() 
    ssc.awaitTermination()
    #ssc.awaitTerminationOrTimeout(10)
    
    #ssc.stop(stopGraceFully = True)
    
    


# def make_plot(counts):
    # """
    # This function plots the counts of positive and negative words for each timestep.
    # """
    # positiveCounts = []
    # negativeCounts = []
    # time = []

    # for val in counts:
	# positiveTuple = val[0]
	# positiveCounts.append(positiveTuple[1])
	# negativeTuple = val[1]
	# negativeCounts.append(negativeTuple[1])

    # for i in range(len(counts)):
	# time.append(i)

    # posLine = plt.plot(time, positiveCounts,'bo-', label='Positive')
    # negLine = plt.plot(time, negativeCounts,'go-', label='Negative')
    # plt.axis([0, len(counts), 0, max(max(positiveCounts), max(negativeCounts))+50])
    # plt.xlabel('Time step')
    # plt.ylabel('Word count')
    # plt.legend(loc = 'upper left')
    # plt.show()

	
def load_wordlist(filename):
    """ 
    This function returns a list or set of words from the given filename.
    """	
    words = {}
    f = open(filename, 'rU')
    text = f.read()
    text = text.split('\n')
    for line in text:
        words[line] = 1
    f.close()
    return words


def wordSentiment(word,pwords,nwords):
    if word in pwords:
	return ('positive', 1)
    elif word in nwords:
	return ('negative', 1)


def updateFunction(newValues, runningCount):
    if runningCount is None:
       runningCount = 0
    return sum(newValues, runningCount) 


def sendRecord(record):
    connection = createNewConnection()
    connection.send(record)
    connection.close()


def stream(ssc, pwords, nwords, duration):
    kstream = KafkaUtils.createDirectStream(
    ssc, topics = ['twitterstream'], kafkaParams = {"metadata.broker.list": 'localhost:9092'})
    tweets = kstream.map(lambda x: x[1].encode("ascii", "ignore"))

    # Each element of tweets will be the text of a tweet.
    # We keep track of a running total counts and print it at every time step.
    words = tweets.flatMap(lambda line:line.split(" "))
    positive = words.map(lambda word: ('Positive', 1) if word in pwords else ('Positive', 0))
    negative = words.map(lambda word: ('Negative', 1) if word in nwords else ('Negative', 0))
    allSentiments = positive.union(negative)
    sentimentCounts = allSentiments.reduceByKey(lambda x,y: x+y)
    runningSentimentCounts = sentimentCounts.updateStateByKey(updateFunction)
    runningSentimentCounts.pprint()
    
    # The counts variable hold the word counts for all time steps
    counts = []
    sentimentCounts.foreachRDD(lambda t, rdd: counts.append(rdd.collect()))
    
    # Start the computation
    ssc.start() 
    ssc.awaitTerminationOrTimeout(duration)
    ssc.stop(stopGraceFully = True)

    return counts


if __name__=="__main__":
    main()