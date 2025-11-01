# es_client = Elasticsearch(
#     "https://6ed9ba20fbcb41ababa8760f7fe85f48.asia-northeast3.gcp.elastic-cloud.com:443",
#     api_key=settings.ES_API_KEY,
# )
from elasticsearch import Elasticsearch

from config import settings

client = Elasticsearch(
    "https://6ed9ba20fbcb41ababa8760f7fe85f48.asia-northeast3.gcp.elastic-cloud.com:443",
    api_key=settings.ES_API_KEY,
)

retriever_object = {
    "standard": {
        "query": {
            "multi_match": {
                "query": "REPLACE WITH YOUR QUERY",
                "fields": [
                    "categories"
                ]
            }
        }
    }
}

search_response = client.search(
    index="seoseung-soo-products",
    retriever=retriever_object,
)
print(search_response['hits']['hits'])