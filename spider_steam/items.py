import scrapy

class SpiderSteamItem(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    number_of_reviews = scrapy.Field()
    rating = scrapy.Field()
    release_date = scrapy.Field()
    developer = scrapy.Field()
    tags = scrapy.Field()
    price_eur = scrapy.Field()
    sale_price_eur = scrapy.Field()
    platforms = scrapy.Field()
