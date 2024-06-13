from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.ml.feature import StopWordsRemover, RegexTokenizer
import findspark
import datetime
import time
from transformers import BertTokenizer, BertForSequenceClassification
import torch

#Model prediction
def predict(text):

     global tokenizer
     global model

     if text is None:
         return -1  
    
     inputs = tokenizer(text, return_tensors="pt")
     labels = torch.tensor([1]).unsqueeze(0)  
     outputs = model(**inputs, labels=labels)
     logits = outputs.logits
     
     probabilities = torch.softmax(logits, dim=-1)
     
     predicted_label = torch.argmax(probabilities, dim=-1).item()
     
     return predicted_label

#Batch processing
def process_batch(batch_df, batch_id):

     global ELASTIC_INDEX
     global ELASTIC_PORT
     global ELASTIC_NODE
     global KIBANA_INDEX
     global stopwords_rm
     global spark_tokenizer
     global tokenizer

     #Logic for labels insertion in DF
     batch_df = batch_df.sort("@timestamp")
     texts_and_timestamps = [(row["@timestamp"], row.text) for row in batch_df.collect()]
     predictions = [{"@timestamp": timestamp, "label": predict(text)} for timestamp, text in texts_and_timestamps]

     schema = StructType([
        StructField("@timestamp", DoubleType()),
        StructField("label", IntegerType())
     ])
     df_predictions = spark.createDataFrame(predictions, schema=schema)
     transformed_df = batch_df.join(df_predictions, "@timestamp", "inner").sort("@timestamp")

     #Data transformation for Kibana
     transformed_df = transformed_df.withColumn("@timestamp", col("@timestamp").cast("timestamp"))
     transformed_df = transformed_df.withColumn("date", date_format(col("@timestamp"), "yyyy-MM-dd'T'HH:mm:ss'Z'"))
     transformed_df = spark_tokenizer.transform(transformed_df)
     transformed_df = stopwords_rm.transform(transformed_df).drop("words").withColumnRenamed("words_filtered", "words")

     #Data insertion in ES indexes
     transformed_df.write.format("console").save() #Debugging
     transformed_df.write.format("es").option("truncate", False) \
          .option("checkpointLocation","/tmp/").option("es.port",ELASTIC_PORT).option("es.nodes",ELASTIC_NODE) \
          .option("es.nodes.wan.only", "false") \
          .option("es.resource", ELASTIC_INDEX).mode("append").save()
     transformed_df.write.format("es").option("truncate", False) \
          .option("checkpointLocation","/tmp/").option("es.port",ELASTIC_PORT).option("es.nodes",ELASTIC_NODE) \
          .option("es.nodes.wan.only", "false") \
          .option("es.resource", KIBANA_INDEX).mode("append").save()


#Loading model
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForSequenceClassification.from_pretrained("tapmodelv2_bert", use_safetensors=True)


KAFKA_BOOTSTRAP_SERVERS = "http://10.0.100.23:9092"
ELASTIC_NODE = "http://10.0.100.25:9200"
ELASTIC_PORT = "9200"
ELASTIC_INDEX = "messages" 
KIBANA_INDEX = "saved_messages"

#Spark configuration
sparkConf = SparkConf().set("es.nodes", "elasticsearch") \
                        .set("es.port", "9200").set("es.nodes.wan.only", "false")


findspark.init()
spark = SparkSession.builder.appName("Bannatore").config(conf=sparkConf) \
          .getOrCreate()


spark.sparkContext.setLogLevel("ERROR")

#Spark pipeline for text processing for Kibana
spark_tokenizer = RegexTokenizer(pattern=r'\s+|[,.\-?!]').setInputCol("text").setOutputCol("words")
stopwords_rm = StopWordsRemover().setInputCol("words").setOutputCol("words_filtered")

time.sleep(10)

#Reading from Kafka
dt = spark \
     .readStream \
     .format("kafka") \
     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
     .option("subscribe", "messaggi").option("startingOffsets", "earliest") \
     .load()

data_schema = StructType().add("message_id", IntegerType()).add("text", StringType()) \
    .add("sender", MapType(keyType=StringType(), valueType=StringType())) \
    .add("date", StringType()).add("chat", StringType()) \
    .add("chat_user", StringType()).add("chat_id", StringType()).add("@timestamp", DoubleType())



data_received = dt.selectExpr("CAST(value AS STRING)") \
     .select(from_json(col("value"), data_schema).alias("data_received")) \
     .select("data_received.*")



# Start the streaming query to ES
query = data_received.writeStream \
     .foreachBatch(process_batch) \
     .option("truncate",False) \
     .start().awaitTermination()





