import json
from itemadapter import ItemAdapter

class SpiderSteamPipeline:
    def open_spider(self, spider):
        self.file = open('found_games.json', 'w')
        with open('dropped_items.log', 'w') as _:
            pass # replace old logs

    def process_item(self, item, spider):
        found_game = json.dumps(ItemAdapter(item).asdict())
        self.file.write(found_game + "\n\n")
        return item

    def close_spider(self, spider):
        self.file.close()
