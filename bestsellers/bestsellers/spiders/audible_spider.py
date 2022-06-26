import scrapy

import json
import csv

class RozetkaSpider(scrapy.Spider):
    name = "audible_amazon"
    start_urls = ['https://www.audible.co.uk/categories?ref=a_search_t1_navTop_pl2cg0c1r7&pf_rd_p=3e9fe0ed-4f01-44f6-a9c2-337a60fefa06&pf_rd_r=DZRBYX584ND67VVA0XVH']

    headers = ["URL","BookType", "BookFormat","Title","Image","AuthorType","AuthorName","ReadType","ReaderName","Publisher","DatePublished","Language","Duration","RatingType",'RatingValue',"RatingCount","Offers type","LowPrice","HighPrice","Price Currency","Breadcrumbs", "description", "allowed_regions"]
    f = open('output.csv', 'w', encoding='utf-8', newline='')
    writer = csv.writer(f, delimiter=";")
    writer.writerow(headers)
    f.close()

    def parse(self, response):
        list_of_car_urls = response.css('h2 a::attr("href")').getall()
        for link in list_of_car_urls:
            link = "https://www.audible.co.uk" + link
            yield response.follow(link, callback=self.find_link_to_cat)

    def find_link_to_cat(self,response):
        link = response.xpath('//a[contains(@class, "allInCategoryPageLink ")]/@href').get()
        yield response.follow(link, callback=self.parse_book_link)

    def parse_book_link(self,response):
        
        page_number = int(response.xpath('//a[contains(@class, "pageNumberElement")]/text()')[-1].get())

        list_of_all_links = response.xpath('//*[@id="product-list-a11y-skiplink-target"]/span/ul/div/li/div/div[1]/div/div[2]/div/div/span/ul/li[1]/h3/a/@href').getall()

        for link_of_book in list_of_all_links:
            yield response.follow(link_of_book, callback=self.parse_page)

        for i in range(2,page_number+1):
            if "&page=" in response.url:
                next_page = response.url.split("&page=")[0] + f"&page={i}&ref"+response.url.split("&ref")[1]
            else:
                next_page= response.url.split("&ref=")[0] + f"&page={i}&ref="+response.url.split("&ref=")[1]
            yield response.follow(next_page, callback=self.parse_book_link)

    def parse_page(self,response):
        script_with_json = response.xpath("//script[contains(@type, 'application/ld+json')]/text()")[1].get()
        json_object = json.loads(script_with_json)
        list_of_keys = json_object[0].keys()
        if "@type" in list_of_keys:
            type = str(json_object[0]["@type"]).replace('"','')
        else:
            type = None
        
        if "bookFormat" in list_of_keys:
            bookFormat = str(json_object[0]["bookFormat"]).replace('"','')
        else:
            bookFormat = None

        if "name" in list_of_keys:
            name = str(json_object[0]["name"]).replace('"','')
        else:
            name = None

        if "description" in list_of_keys:
            description = str(json_object[0]["description"]).replace('"','')
        else:
            description = None

        if "image" in list_of_keys:
            image = str(json_object[0]["image"]).replace('"','')
        else:
            image = None

        if "author" in list_of_keys:
            try:
                author_type = str(json_object[0]["author"][0]["@type"]).replace('"','')
            except:
                author_type = None
            try:
                author_name = str(json_object[0]["author"][0]["name"]).replace('"','')
            except:
                author_name = None
        else:
            author_type = None
            author_name = None

        if "readBy" in list_of_keys:
            try:
                reader_type = str(json_object[0]["readBy"][0]["@type"]).replace('"','')
            except:
                reader_type = None
            try:
                reader_name =  str(json_object[0]["readBy"][0]["name"]).replace('"','')
            except:
                reader_name = None
        else:
            reader_type = None
            reader_name = None

        if "publisher" in list_of_keys:
            publisher = str(json_object[0]["publisher"]).replace('"','')
        else:
            publisher = None

        if "datePublished" in list_of_keys:
            datePublished = str(json_object[0]["datePublished"]).replace('"','')
        else:
            datePublished = None

        if "inLanguage" in list_of_keys:
            inLanguage = str(json_object[0]["inLanguage"]).replace('"','')
        else:
            inLanguage = None


        if "duration" in list_of_keys:
            duration = str(json_object[0]["duration"]).replace('"','')
        else:
            duration = None

        if "regionsAllowed" in list_of_keys:
            allowed_regions = ""
            len_of_allowed_regions = len(json_object[0]["regionsAllowed"])
            for i in range(0, len_of_allowed_regions):
                if i != len_of_allowed_regions-1:
                    allowed_regions = allowed_regions + str(json_object[0]["regionsAllowed"][i]).replace('"','')+"|"
                else:
                    allowed_regions = allowed_regions + str(json_object[0]["regionsAllowed"][i]).replace('"','')


        else:
            allowed_regions = None


        if "aggregateRating" in list_of_keys:
            try:
                Rating_type= str(json_object[0]["aggregateRating"]["@type"]).replace('"','')
            except:
                Rating_type=  None
            
            try:
                ratingValue = str(json_object[0]["aggregateRating"]["ratingValue"]).replace('"','')
            except:
                ratingValue =  None

            try:
                ratingCount = str(json_object[0]["aggregateRating"]["ratingCount"]).replace('"','')
            except:
                ratingCount =  None
        else:
            Rating_type = None
            ratingValue =  None
            ratingCount =  None

        if "offers" in list_of_keys:
            try:
                offers_type= str(json_object[0]["offers"]["@type"]).replace('"','')
            except:
                offers_type = None
        
            try:
                lowPrice = str(json_object[0]["offers"]["lowPrice"]).replace('"','')
            except:
                lowPrice = None

            try:
                highPrice = str(json_object[0]["offers"]["highPrice"]).replace('"','')
            except:
                highPrice = None
            
            try:
                priceCurrency = str(json_object[0]["offers"]["priceCurrency"]).replace('"','')
            except:
                priceCurrency = None
        else:
            offers_type = None
            lowPrice = None
            highPrice = None
            priceCurrency = None


        keys_in_BreadcrumbList = json_object[1].keys()
        
        if "itemListElement" in  keys_in_BreadcrumbList:
            items_dict = json_object[1]["itemListElement"]
            count_of_items_element =  len(items_dict)
            list_of_items = []
            Breadcrumbs = ""
            for i in range(1,count_of_items_element):
                if i != count_of_items_element-1:
                    Breadcrumbs = Breadcrumbs+str(json_object[1]["itemListElement"][i]["item"]["name"]).replace('"','')+"|"
                else:
                    Breadcrumbs = Breadcrumbs+str(json_object[1]["itemListElement"][i]["item"]["name"]).replace('"','')
        else:
            Breadcrumbs = None


        list_to_writer = [response.url ,type, bookFormat,name,image,author_type,author_name,reader_type,reader_name,publisher,datePublished,inLanguage, duration,  Rating_type,ratingValue,ratingCount,offers_type,lowPrice,highPrice,priceCurrency,Breadcrumbs, description, allowed_regions]

        f = open('output.csv', 'a', encoding='utf-8', newline='')
        writer = csv.writer(f, delimiter=";")
        writer.writerow(list_to_writer)
        f.close()

