import scrapy
import yaml
from scrapy.exceptions import CloseSpider
from cleaner import clean_with_trafilatura  # Corrected import


class Crawl4AI(scrapy.Spider):
    name = "crawl4ai_spider"

    def __init__(self, *args, **kwargs):
        super(Crawl4AI, self).__init__(*args, **kwargs)
        try:
            with open("configs/websites.yaml", 'r') as f:
                configs = yaml.safe_load(f)

            self.websites = {site['name']: site for site in configs['websites']}
            self.target_site = self.websites.get(kwargs.get('site'))

            if not self.target_site:
                raise CloseSpider(f"Site '{kwargs.get('site')}' not found in config.")

            self.start_urls = self.target_site['start_urls']
            self.crawl_depth = self.target_site['crawl_depth']
            self.allowed_domains = [url.split('//')[-1].split('/')[0] for url in self.start_urls]

        except FileNotFoundError:
            raise CloseSpider("websites.yaml not found. Please create the config file.")

    def parse(self, response):
        current_depth = response.meta.get('depth', 0)

        cleaned_content = clean_with_trafilatura(response.text)

        if response.css(self.target_site['rules']['extract'][0]):
            item = {
                'url': response.url,
                'title': response.css('title::text').get(),
                'raw_html': response.text,
                'clean_text': cleaned_content,
                'publish_date': None,  # Placeholder, needs a specific selector
                'author': None  # Placeholder, needs a specific selector
            }
            yield item

        if current_depth < self.crawl_depth:
            links_to_follow = response.css(self.target_site['rules']['follow'][0] + '::attr(href)').getall()
            for link in links_to_follow:
                yield response.follow(link, self.parse, meta={'depth': current_depth + 1})