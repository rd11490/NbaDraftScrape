class MapOfList:
    def __init__(self):
        self.map_collection = {}

    def add(self, key, value):
        if key not in self.map_collection.keys():
            self.map_collection[key] = []
        self.map_collection[key].extend(value)


    def print(self):
        for k in self.map_collection.keys():
            print(k)
            for l in self.map_collection[k]:
                print(l)