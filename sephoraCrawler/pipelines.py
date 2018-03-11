import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class SephoracrawlerPipeline(object):
    def __init__(self):
        collection = pymongo.MongoClient(
            settings['MONGO_SERVER'],
            settings['MONGO_PORT']
        )
        self.db = collection[settings['MONGO_DB']]
        self.collection = self.db[settings['MONGO_COLL']]
        self.ten_skincare_ingredients_to_avoid = ['lead', 'triclosan', 'oxybenzone', 'bht',
                                                  'butylated hydroxyanisole', 'bha',
                                                  'butylated hydroxytoluene', 'coal tar', 'paraben', 'phthalates',
                                                  'formaldehyde',
                                                  'eda', 'dithanolamine', 'triethanolamine', 'toluene', 'retinoids',
                                                  'retin a',
                                                  'salycylic acid', 'bpa', 'bithionol',
                                                  'chlorofluorocarbon propellants', 'chloroform',
                                                  'hexachlorophene', 'mercury', 'methylene chloride', 'vinyl chloride',
                                                  'zirconium', 'talc']

    def process_item(self, item, spider):
        print("================Pipelines works!==============")
        valid = True
        for data in item:
            if not data:
                raise DropItem("Missing {0}!".format(data))
        if valid:
            unsafe_ingredients = self.check_safety(item['ingredients'])
            if unsafe_ingredients:
                item['unsafe_ingredients'] = unsafe_ingredients
                item['is_safe'] = False
            self.collection.insert(dict(item))

        return item

    def check_safety(self, ingredients):
        if not ingredients:
            return []
        contain_unsafe_ingredients = []
        for unsafe_ingredient in self.ten_skincare_ingredients_to_avoid:
            for tuples in ingredients:
                if unsafe_ingredient in tuples.lower():
                    contain_unsafe_ingredients.append(unsafe_ingredient)
        return contain_unsafe_ingredients
