import scrapy
from collections import defaultdict


class CoronaSpiderSpider(scrapy.Spider):
    name = "coronaspider"
    allowed_domains = ["www.worldometers.info"]
    start_urls = ["https://www.worldometers.info/coronavirus"]

    def parse(self, response):
        # Selecting the table where the data is contained using XPath
        corona_table = response.xpath('//table[@id="main_table_countries_today"]')

        # Extracting the column headers
        column_headers = corona_table.xpath('.//tr/th')

        hs = ""
        # Printing each content of <th> on a single line
        for header in column_headers:
            # Extracting all text content within <th> and concatenating them into one line
            header_text = ''.join(header.xpath('.//text()').getall())
            hs +=  header_text.strip() + '\n'
            
        # print(self.get_column_names(hs))
        column_names = self.get_column_names(hs)
        
        # Extracting rows respecting specified column grouping
        # print(corona_table.xpath('.//tr[@style=""]')[0].get())
                
        countries_data = defaultdict(dict)
        
        # print(formatted_output)
        
        for tr in corona_table.xpath('.//tr[@style=""]'):
            td_elements = tr.xpath('.//td')
            td_contents = [td.xpath('string()').get().strip() for td in td_elements]
            td = '\n'.join(td_contents)
            line = self.get_country_data(td)
            # print(line)
            
            countries_data[line[0]] = dict(zip(column_names, line[1:]))
            
            # print(countries_data)

        yield countries_data
    
    def get_column_names(self, tr):
        """
        This function return a well formatted list for the column names.
        """
        line = tr.strip("\n#").strip().split("\n")
        line[12] += line[13]
        line[12] = ''.join(line[12].split())
        line[16] = line[16] + line[17] + line[18]
        line.pop(13)
        line.pop(16)
        line.pop(16)
        return line[1:-1]
    
    def get_country_data(self, country_line):
        """
        This function formats a given input line parsed from an html page.

        Parameters:
            country_line : str
                it is a row table row, that contains the data.

        Returns:
            line : list
                A list containing all the useful information retrieved.
        """
        import re
        line = country_line.strip().split("\n")
        line.pop(0)
        
        line[15] = line[15] + line[16] + line[17]
        line.pop(16)
        line.pop(16)
        
        for i, element in zip(range(len(line)), line):
            if re.search("[1-9]+", element):
                line[i] = float(''.join(line[i].strip('+').split(",")))
            else:
                pass

        return line[:-1]
                
        
