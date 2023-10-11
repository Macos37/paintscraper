# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
from paintscraper.items import PaintscraperItem

class PaintscraperPipeline:
    def open_spider(self, spider):
        self.dataframe = pd.DataFrame(columns=['name', 'price', 'description']) 

    def close_spider(self, spider):
        self.dataframe.to_csv('products.csv', index=False)

    def process_item(self, item: PaintscraperItem, spider):
        df_temp = pd.DataFrame([dict(item)])
        self.dataframe = pd.concat([self.dataframe, df_temp])
        return item