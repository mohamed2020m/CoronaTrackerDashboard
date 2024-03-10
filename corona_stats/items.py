# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CoronaStatsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    country = scrapy.Field()
    total_cases = scrapy.Field()
    new_cases = scrapy.Field()
    total_deaths = scrapy.Field()
    new_deaths = scrapy.Field()
    total_recovered = scrapy.Field()
    new_recovered = scrapy.Field()
    active_cases = scrapy.Field()
    serious_critical = scrapy.Field()
    total_cases_per_million = scrapy.Field()
    deaths_per_million = scrapy.Field()
    total_tests = scrapy.Field()
    tests_per_million = scrapy.Field()
    population = scrapy.Field()
    continent = scrapy.Field()
