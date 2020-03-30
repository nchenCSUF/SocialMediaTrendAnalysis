import json
import sys
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql.context import SQLContext
import pysolr


def send2solr(solr,rdd):
    tweet=json.loads(rdd)

    index = [{
        "created_at": tweet["created_at"],
        "id": tweet["id_str"],
        "text": tweet["text"],
        "user_name": tweet["screen_name"],
        "lan":-118.668404,
        "lng":33.704538
    }]
    solr.add(index, commit=True)
    solr.commit()
    print("Success")
    return index

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: KafkaSparkStreaming.py <zk> <topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="SocialMediaTrendAnalysis")
    ssc = StreamingContext(sc, 20)

    zkQuorum, topic = sys.argv[1:]
    kvs = KafkaUtils.createStream(ssc, zkQuorum, "Twitter-streaming", {topic: 1})
    solr = pysolr.Solr('http://192.168.36.130:8886/solr/geoTwitterdata',timeout=20)
    lines = kvs.map(lambda x: send2solr(solr,x[1])).count()

    #Sample word count program to check tweets are read from kafka
    #counts = lines.flatMap(lambda line: line.split(" ")) \
     #             .map(lambda word: (word, 1)) \
      #            .reduceByKey(lambda a, b: a+b)
    #counts.pprint()

    ssc.start()
    ssc.awaitTermination()