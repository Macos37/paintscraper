import json
from typing import Any
import scrapy
from scrapy.http import Response
from paintscraper.items import PaintscraperItem


class PaintspiderSpider(scrapy.Spider):
    name = "paintspider"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]

    def parse_item(self, item) -> dict:
        new_item = PaintscraperItem()
        new_item['name'] = item.xpath(".//span[@itemprop='name']/text()").get()
        new_item['price'] = item.xpath(".//span[@itemprop='price']/text()").get()
        new_item['description'] = item.xpath(".//span[@class='span-specifications-more']/text() \
              | .//span[@class='span-specifications-more']/br/following-sibling::text()").extract()
        return new_item
    
    def parse(self, response: Response):
        categories = response.xpath('//div[@id="5940"]//a[not(@style="display: none;")]')
        for category in categories:
            category_name = category.xpath('.//text()').get()
            if category_name in ["Краски и материалы специального назначения",
                                 "Краски для наружных работ", "Лаки"]:
                category_link = category.xpath('.//@href').get()
                yield response.follow(category_link, callback=self.parse_products)
                

    def parse_products(self, response: Response):
        products = response.xpath('//div[@class="horizontal-product-items"]')
        for product in products:
            product_content = product.xpath('.//div[@class="horizontal-product-item-container"]')
            for product in product_content:
                item = self.parse_item(product)
                item_id = product.xpath(".//span[@class='span-specifications']/a/@data-item").get()
                yield scrapy.FormRequest(
                    url="https://order-nn.ru/local/ajax/kmo/getItemSpecifications.php", 
                    formdata={'type': 'specifications', 'item': item_id}, 
                    callback=self.parse_specifications, 
                    meta={'item': item})
            next_page = response.xpath(".//li[@class='active']/following-sibling::li/a/@href").get()
            if next_page:
                yield response.follow(next_page, callback=self.parse_products)
                
                
                
    def parse_specifications(self, response: Response):
        item = response.meta['item']
        specifications = {}
        spec_rows = response.xpath('//table[@class="table table-striped"]/tr')
        for row in spec_rows:
            name = row.xpath("./td[1]/text()").get()
            value = row.xpath("./td[2]/text()").get()
            if name and value:
                specifications[name.strip()] = value.strip()
        item['specifications'] = json.dumps(specifications, ensure_ascii=False)
        yield item