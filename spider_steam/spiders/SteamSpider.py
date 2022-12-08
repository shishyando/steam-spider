import scrapy
from spider_steam.items import SpiderSteamItem
from urllib.parse import urlencode
import re

class SteamspiderSpider(scrapy.Spider):
    name = "SteamSpider"
    allowed_domains = ["store.steampowered.com"]
    queries = ["portal", "Half-Life", "first person shooter"]
    page_num = 2


    def url_constructer(self, query, page):
        # cgi = {"term": query, "page": page, "sort_by": "Reviews_DESC", "ndl": "1"}
        cgi = {"term": query, "page": page, "sort_by": "", "ndl": "1"}
        return "https://store.steampowered.com/search/?" + urlencode(cgi)

    def start_requests(self):
        for query in self.queries:
            for page in range(1, self.page_num + 1):
                url = self.url_constructer(query, page)
                yield scrapy.Request(url=url, callback=self.find_games)
            # sleep(10)


    def find_games(self, response):
        found_games = set()
        for res in response.xpath('//div[@id = "search_result_container"]//a/@href'):
            if "app" in res.get():
                found_games.add(res.get())

        for game in found_games:
            yield scrapy.Request(url=game, callback=self.parse)

    def parse(self, response):
        item = SpiderSteamItem()
        name = response.xpath('//div[@class="apphub_AppName"]/text()')
        if not len(name) > 0:
            yield None

        try:
            item['name'] = name[0].get()
            item['category'] = get_categories(response)
            item['number_of_reviews'] = get_number_of_reviews(response)
            item['rating'] = get_rating(response)
            item['release_date'] = get_release_date(response)
            item['developer'] = get_developer(response)
            item['tags'] = get_tags(response)
            item['price_eur'] = get_price(response)
            item['sale_price_eur'] = get_sale_price(response)
            item['platforms'] = get_platforms(response)
        except Exception as e:
            with open("dropped_items.log", "a") as logs:
                logs.write(e)
            yield None
        yield item


def get_categories(response):
    categories = response.xpath('//div[@class = "blockbg"]/*/text()')
    categories = [category.get().strip() for category in categories]
    categories = categories[1:]
    return categories if len(categories) > 0 else None


def get_rating(response):
    rating = response.xpath('//meta[@itemprop = "ratingValue"]/@content')
    return rating[0].get() if len(rating) > 0 else None


def get_number_of_reviews(response):
    number_of_reviews = response.xpath('//meta[@itemprop = "reviewCount"]/@content')
    return number_of_reviews[0].get() if len(number_of_reviews) > 0 else None


def get_release_date(response):
    release_date = response.xpath('//div[@class="release_date"]/div[@class="date"]/text()')
    return release_date[0].get() if len(release_date) > 0 else None


def get_developer(response):
    developers = response.xpath('//div[@class="dev_row"]/div[@class="summary column"]/*/text()')
    return developers[0].get() if len(developers) > 0 else None


def get_tags(response):
    tags = response.xpath('//div[@class="glance_tags popular_tags"]/*/text()')
    tags_with_plus = [tag.get().strip() for tag in tags]
    return tags_with_plus[:-1]


price_re = re.compile(r"(\d+\,?\d*)(.*)")
def price_parser(price_str):
    return re.sub(price_re, r'\1', price_str)


def get_price(response):
    prices = response.xpath('//div[@class = "game_area_purchase_game_wrapper"]//div[@class="discount_original_price"]/text()')
    if len(prices) == 0:
        prices = response.xpath('//div[@class = "game_area_purchase_game_wrapper"]//div[@class="game_purchase_price price"]/text()')
    return price_parser(prices[0].get().strip()) if len(prices) > 0 else None


def get_sale_price(response):
    sale_prices = response.xpath('//div[@class = "game_area_purchase_game_wrapper"]//div[@class = "discount_final_price"]/text()')
    return price_parser(sale_prices[0].get().strip()) if len(sale_prices) > 0 else None


platform_re = re.compile(r"(platform_img )(\w+)")
def get_platforms(response):
    platforms = response.xpath('//div[@class="game_area_purchase_game_wrapper"]//span[contains(@class, "platform_img")]/@class')
    platforms = [p.get().strip() for p in platforms]
    platforms = [re.sub(platform_re, r'\2', p) for p in platforms]
    return list(set(platforms))
