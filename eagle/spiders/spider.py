import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import EagleItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class EagleSpider(scrapy.Spider):
	name = 'eagle'
	start_urls = ['https://www.eaglebank.com/news-more/']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="older-newer"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="news-date"]/text()').get()
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="entry-content"]//text()[not (ancestor::div[@class="title-date-share"] or ancestor::div[@class="prev-next-navigation"] or ancestor::a or ancestor::div[@class="vc_row wpb_row vc_row-fluid vc_custom_1606754266926 vc_row-has-fill"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=EagleItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
