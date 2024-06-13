import asyncio
import time
from elasticsearch import Elasticsearch
from telegram.ext import (
    Application
)

FLUENT_URL = "http://10.0.100.21:5050"


ELASTIC_NODE = "http://10.0.100.25:9200"
ELASTIC_PORT = "9200"
ELASTIC_INDEX = "messages"

es = Elasticsearch(hosts=ELASTIC_NODE) 

#Message eraser
async def delete_messages():

    application = Application.builder().token("***REMOVED***").build()
    match_bannables = {
        "match": {"label": 1}
    }

    match_not_bannables = {
        "match": {"label": 0}
    }
    

    while True:
        try:
            #Query incoming messages from ES index messages
            response = es.search(index=ELASTIC_INDEX, query=match_bannables, size=10000)
            ids = [hit["_id"] for hit in response["hits"]["hits"]]

            delete_query = {"terms": {
                    "_id": ids
                }
            }

            #Delete retrieved messages and not bannable messages from ES index messages
            es.delete_by_query(index=ELASTIC_INDEX, query=delete_query)
            es.delete_by_query(index=ELASTIC_INDEX, query=match_not_bannables)

            hits = response["hits"]["hits"]

            print(f"Got {len(hits)} hits:")

            #Delete every message hitted from chats
            for hit in hits:
                delete_text = f"Il messaggio '{hit['_source']['text']}', inviato dall'utente '{hit["_source"]["sender"]["username"]}', è stato rimosso perchè considerato offensivo"
                await application.bot.send_message(chat_id=hit["_source"]["chat_id"], reply_to_message_id=hit["_source"]["message_id"], text=delete_text)

                await application.bot.deleteMessage(message_id = hit["_source"]["message_id"],
                                        chat_id = hit["_source"]["chat_id"]) #se il classificatore mi dice bannabile lo cancello """
                    # mando un messaggio all'utente dicendogli che il messaggio è stato rimosso
            time.sleep(0.5)
        except Exception as e:
            continue


    
    
if __name__ == "__main__":
    asyncio.run(delete_messages())