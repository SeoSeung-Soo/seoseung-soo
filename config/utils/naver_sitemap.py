from xml.etree import ElementTree

from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from config import settings
from products.models import Product
from products.utils.url_slug import product_name_to_slug


def sitemap(request: HttpRequest) -> HttpResponse:
    host_url = getattr(settings, 'HOST_URL', 'https://seoseung-soo.com')
    
    # XML 네임스페이스 설정
    urlset = ElementTree.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # 홈 페이지
    url_elem = ElementTree.SubElement(urlset, 'url')
    ElementTree.SubElement(url_elem, 'loc').text = f"{host_url}/"
    ElementTree.SubElement(url_elem, 'lastmod').text = timezone.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
    ElementTree.SubElement(url_elem, 'priority').text = '1.0'
    
    # 상품 목록 페이지
    url_elem = ElementTree.SubElement(urlset, 'url')
    ElementTree.SubElement(url_elem, 'loc').text = f"{host_url}/products/list/"
    ElementTree.SubElement(url_elem, 'lastmod').text = timezone.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
    ElementTree.SubElement(url_elem, 'priority').text = '0.9'
    
    # 카테고리 목록 페이지
    url_elem = ElementTree.SubElement(urlset, 'url')
    ElementTree.SubElement(url_elem, 'loc').text = f"{host_url}/categories/list/"
    ElementTree.SubElement(url_elem, 'lastmod').text = timezone.now().strftime('%Y-%m-%dT%H:%M:%S+09:00')
    ElementTree.SubElement(url_elem, 'priority').text = '0.8'
    
    # 모든 활성 상품 페이지
    products = Product.objects.filter(is_live=True, is_sold=False).only(
        'name', 'updated_at'
    ).order_by('-updated_at')
    
    for product in products:
        url_elem = ElementTree.SubElement(urlset, 'url')
        product_slug = product_name_to_slug(product.name)
        ElementTree.SubElement(url_elem, 'loc').text = f"{host_url}/products/{product_slug}/"
        ElementTree.SubElement(url_elem, 'lastmod').text = product.updated_at.strftime('%Y-%m-%dT%H:%M:%S+09:00')
        ElementTree.SubElement(url_elem, 'priority').text = '0.8'
    
    # XML 문자열 생성
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += ElementTree.tostring(urlset, encoding='unicode')
    
    response = HttpResponse(xml_str, content_type='application/xml; charset=utf-8')
    return response
