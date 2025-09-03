from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawlers.spider import Crawl4AI
import pandas as pd
import json
import os
from validator import validate_schema, post_process_data


def run_crawler(site_name, num_urls=5):
    settings = get_project_settings()

    settings['CLOSESPIDER_ITEMCOUNT'] = num_urls
    settings['FEED_FORMAT'] = 'json'
    settings['FEED_URI'] = 'data/output.json'

    process = CrawlerProcess(settings)
    process.crawl(Crawl4AI, site=site_name)
    process.start()


def process_and_report():
    output_path = 'data/output.json'
    if not os.path.exists(output_path) or os.stat(output_path).st_size == 0:
        print("No valid output file found. The crawler might have failed to scrape any items.")
        # Create an empty DataFrame to avoid errors in the next steps
        df = pd.DataFrame(
            columns=['url', 'title', 'publish_date', 'author', 'raw_html', 'clean_text', 'is_empty_or_short',
                     'is_duplicate'])
    else:
        # Load the JSON lines file
        with open(output_path, 'r') as f:
            data = [json.loads(line) for line in f]

        validated_data = [d for d in data if validate_schema(d)]
        df = pd.DataFrame(validated_data)

    # Perform quality checks, even if the DataFrame is empty
    if not df.empty:
        df['is_empty_or_short'] = df['clean_text'].apply(lambda x: post_process_data(x, min_length=150))
        df['is_duplicate'] = df.duplicated(subset='clean_text', keep='first')

    if not os.path.exists('data/reports'):
        os.makedirs('data/reports')

    report_path = 'data/reports/scraper_report.csv'
    df.to_csv(report_path, index=False)
    print(f"Report saved to {report_path}")


if __name__ == '__main__':
    run_crawler(site_name="sample_news_site", num_urls=5)

    process_and_report()