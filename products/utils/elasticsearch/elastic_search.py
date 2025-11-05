from typing import Any, Dict, List

from elasticsearch import Elasticsearch, helpers

from config import settings
from products.utils.elasticsearch.elastic_services import ElasticSearchService

es_client = Elasticsearch(
    settings.ES_HOST,
    api_key=settings.ES_API_KEY,
)

PRODUCT_INDEX_NAME = "seoseung-soo-products"


def create_product_index(force_reset: bool = False) -> None:
    category_synonyms = ElasticSearchService.load_category_synonyms()
    color_synonyms = ElasticSearchService.load_color_synonyms()
    
    index_mapping = {
        "settings": {
            "analysis": {
                "filter": {
                    "category_synonym_filter": {
                        "type": "synonym",
                        "synonyms": category_synonyms,
                    },
                    "color_synonym_filter": {
                        "type": "synonym",
                        "synonyms": color_synonyms,
                    }
                },
                "analyzer": {
                    "category_analyzer": {
                        "type": "custom",
                        "tokenizer": "keyword",
                        "filter": ["lowercase", "category_synonym_filter"]
                    },
                    "color_analyzer": {
                        "type": "custom",
                        "tokenizer": "keyword",
                        "filter": ["lowercase", "color_synonym_filter"]
                    },
                    "text_with_synonym_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "category_synonym_filter"]
                    },
                    "text_with_color_synonym_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "category_synonym_filter", "color_synonym_filter"]
                    },
                    "korean_analyzer": {
                        "type": "standard",
                        "filter": ["lowercase"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "name": {
                    "type": "text",
                    "analyzer": "korean_analyzer",
                    "fields": {
                        "synonym": {"type": "text", "analyzer": "text_with_synonym_analyzer"}
                    }
                },
                "description": {
                    "type": "text",
                    "analyzer": "korean_analyzer",
                    "fields": {
                        "synonym": {"type": "text", "analyzer": "text_with_synonym_analyzer"}
                    }
                },
                "price": {"type": "float"},
                "sale_price": {"type": "float"},
                "stock": {"type": "integer"},
                "is_live": {"type": "boolean"},
                "is_sold": {"type": "boolean"},
                "categories": {
                    "type": "keyword",
                    "fields": {
                        "text": {"type": "text", "analyzer": "category_analyzer"}
                    }
                },
                "colors": {
                    "type": "keyword",
                    "fields": {
                        "text": {"type": "text", "analyzer": "color_analyzer"}
                    }
                },
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        }
    }
    
    if not es_client.indices.exists(index=PRODUCT_INDEX_NAME):
        es_client.indices.create(index=PRODUCT_INDEX_NAME, body=index_mapping)
    elif force_reset:
        try:
            es_client.indices.delete(index=PRODUCT_INDEX_NAME)
        except Exception:
            pass  # Index doesn't exist, ignore
        es_client.indices.create(index=PRODUCT_INDEX_NAME, body=index_mapping)
        


def bulk_index_products(products: Any, reset_index: bool = False) -> tuple[int, int]:
    create_product_index(force_reset=reset_index)
    actions = []
    for product in products:
        doc = {
            "_index": PRODUCT_INDEX_NAME,
            "_id": product.id,
            "_source": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "sale_price": float(product.sale_price) if product.sale_price else None,
                "stock": product.stock,
                "is_live": product.is_live,
                "is_sold": product.is_sold,
                "categories": [cat.name for cat in product.categories.all()],
                "colors": [color.name for color in product.colors.all()],
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat(),
            }
        }
        actions.append(doc)
    
    if actions:
        result = helpers.bulk(es_client, actions, raise_on_error=False)
        if isinstance(result, tuple):
            success, failed = result
            failed_count = len(failed) if isinstance(failed, list) else 0
            return success, failed_count
        return len(actions), 0
    
    return 0, 0


def search_products(query: str, limit: int = 100) -> List[Dict[str, Any]]:
    if not query:
        return []
    
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "name^5", "name.synonym^5",
                                "description^3", "description.synonym^3",
                                "categories.text^10",
                                "colors.text^8"
                            ],
                            "type": "best_fields",
                            "analyzer": "text_with_color_synonym_analyzer",
                            "fuzziness": "AUTO",
                        }
                    }
                ],
                "filter": [
                    {"term": {"is_live": True}},
                    {"term": {"is_sold": False}}
                ]
            }
        },
        "size": limit,
        "sort": [
            {"created_at": {"order": "desc"}}
        ]
    }
    
    try:
        response = es_client.search(index=PRODUCT_INDEX_NAME, body=search_body)
        product_ids = [hit["_source"]["id"] for hit in response["hits"]["hits"]]
        return product_ids
    except Exception:
        return []


def delete_product_from_index(product_id: int) -> None:
    try:
        es_client.delete(index=PRODUCT_INDEX_NAME, id=str(product_id))
    except Exception:
        pass  # Index doesn't exist, ignore