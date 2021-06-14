This assignment was a part of the cloud computing course. In this assignment, we had to fetch the tweets based on a particular location and do the further processing.

Apply for Twitter developer account. Once done, create an application and fetch the following credentials which are needed to use twitter APIs
consumer_key, consumer_secret, access_token, access_token_secret

Download the following python packages as they are pre-requisite for running the main program
kafka-python, oauthlib, requests, requests-oauthlib, six, tweepy, flask

Also ensure Kafka and zookeeper are installed and they are up and running.
nohup kafka/bin/zookeeper-server-start.sh kafka/config/zookeeper.properties > zoo.log &
nohup kafka/bin/kafka-server-start.sh kafka/config/server.properties > ka.log &

First we need to create topics in Kafka for NY and CA.
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic NY
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic CA

We need to invoke program which read tweets based on locations NY and CA and pushes them to Kafka
python read_tweets.py NY
python read_tweets.py CA

Then we have to invoke the program that performs the analysis on the tweets after consuming it from Kafka.
$SPARK_HOME/bin/spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.4.5.jar --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:2.4.5 twitter_stream.py NY

To run the web application we need to invoke the following command:
python app.py

A detailed report regarding installation and the next steps are available in Report.pdf