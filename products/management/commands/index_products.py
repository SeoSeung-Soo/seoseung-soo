from typing import Any

from django.core.management.base import BaseCommand

from products.models import Product
from products.utils.elasticsearch.elastic_search import bulk_index_products


class Command(BaseCommand):
    help = 'Index all products in Elasticsearch'

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-indexing of all products',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        products = Product.objects.filter(is_live=True).prefetch_related('categories', 'colors')
        
        self.stdout.write(f'Indexing {products.count()} products...')
        
        success_count, failed_count = bulk_index_products(products, reset_index=options['force'])
        
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully indexed {success_count} products')
            )
        
        if failed_count > 0:
            self.stdout.write(
                self.style.WARNING(f'Failed to index {failed_count} products')
            )
        
        self.stdout.write(self.style.SUCCESS('Indexing complete!'))

