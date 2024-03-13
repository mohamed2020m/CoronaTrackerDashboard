from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from corona_stats.spiders.coronaspider import CoronaSpiderSpider
from corona_stats.spiders.totalStatscoronapider import TotalstatscoronapiderSpider


# Global variable to store scraped data
scraped_data = []

# Handler function to process scraped data
def item_scraped(item, response, spider):
    scraped_data.append(item)

# Function to initialize and run the scrapy process with multiple spiders
def run_all_spiders(spider_classes):
    process = CrawlerProcess()
    
    # Connect the item_scraped function to the item_scraped signal
    dispatcher.connect(item_scraped, signal=signals.item_scraped)
    
    # Loop through the provided spider classes and add them to the crawl process
    for spider_class in spider_classes:
        process.crawl(spider_class)
        
    # Start the crawling process
    process.start()  # Automatically stops after all spiders have finished

# Function to run spiders and return scraped data
def get_scraped_data():
    # List of spider classes to run
    spiders_to_run = [CoronaSpiderSpider, TotalstatscoronapiderSpider]
    run_all_spiders(spiders_to_run)
    return scraped_data
