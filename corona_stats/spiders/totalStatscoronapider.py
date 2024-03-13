import scrapy

class TotalstatscoronapiderSpider(scrapy.Spider):
    name = "totalStatscoronapider"
    allowed_domains = ["www.worldometers.info"]
    start_urls = ["https://www.worldometers.info/coronavirus"]

    def parse(self, response):
        countries_data = dict()
        
        totalCases = response.xpath('//div[@class="maincounter-number"]/span/text()')[0].extract()
        totalDeaths = response.xpath('//div[@class="maincounter-number"]/span/text()')[1].extract()
        totalRecovered = response.xpath('//div[@class="maincounter-number"]/span/text()')[2].extract()
        
        # print(totalCases)

        countries_data["TotalCase"] =  totalCases
        countries_data["TotalDeaths"] = totalDeaths
        countries_data["TotalRecovered"] = totalRecovered
        
        yield countries_data