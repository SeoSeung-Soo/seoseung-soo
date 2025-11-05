import os
from typing import List


class ElasticSearchService:
    @staticmethod
    def load_synonyms(filename: str) -> List[str]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        synonyms_file = os.path.join(current_dir, "es_data", filename)

        try:
            with open(synonyms_file, 'r', encoding='utf-8') as f:
                synonyms = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            return synonyms
        except FileNotFoundError:
            return []

    @staticmethod
    def load_category_synonyms() -> List[str]:
        return ElasticSearchService.load_synonyms("category_synonyms")

    @staticmethod
    def load_color_synonyms() -> List[str]:
        return ElasticSearchService.load_synonyms("color_synonyms")