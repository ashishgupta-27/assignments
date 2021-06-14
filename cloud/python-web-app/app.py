from flask import Flask, render_template
import os
app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')
    
@app.route("/NY")
def fetchTweetDataNY():
    cmd='$SPARK_HOME/bin/spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.4.5.jar --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:2.4.5 twitter_stream.py NY'
    os.system(cmd)
    #file1 = open('/home/cs19m012/out.txt', 'r')
    # lines = file1.readlines()
    
    # word='Total tweets'
    # for line in lines:
        # if word in line:
            # return line
    return "Fetching tweets from NY"
    
@app.route("/CA")
def fetchTweetDataCA():
    cmd='$SPARK_HOME/bin/spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.4.5.jar --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:2.4.5 twitter_stream.py CA'
    os.system(cmd)
    return "Fetching tweets from CA"
	
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
	