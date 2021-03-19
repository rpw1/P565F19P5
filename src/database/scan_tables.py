from user_database import UserDatabase
from content_database import ContentDatabase
import math

class ScanTables:

    def __init__(self):
        self.u_db = UserDatabase()
        self.c_db = ContentDatabase()
        self.user_scan_items = ['first_name', 'last_name', 'username', 'location', 'specialties', 'gender']

    def list_get(self, current_list, index):
        item = None
        try:
            item = current_list[index]
        except Exception as e:
            item = None
        return item

    def compareItems(self, search_tag, database_item):
        search_tag_char = [char for char in search_tag.upper()]
        database_item_char = [char for char in database_item.upper()]
        digit_difference = len(search_tag_char) - len(database_item_char)
        index_count = len(database_item_char) if digit_difference < 0 else len(search_tag_char)
        accrue_value = 0
        for index in range(index_count):
            s_val = self.list_get(search_tag_char, index)
            d_val = self.list_get(database_item_char, index)
            if s_val == None or d_val == None:
                break
            accrue_value += abs(ord(s_val) - ord(d_val))
        return accrue_value + (math.exp(abs(digit_difference)) / 3)

    def full_scan(self, search_tag):
        items = []
        heuristics = []
        search_dict = dict()
        for user in self.u_db.scan_table():
            user_email = user['email']
            for key, value in user.items():
                if key == 'specialties':
                    for specialty in value:
                        items.append(specialty)
                        heuristics.append(self.compareItems(search_tag, specialty))
                elif key in self.user_scan_items:
                    items.append(user_email + "$%$" + value)
                    heuristics.append(self.compareItems(search_tag, value))
        search_results = [(x,_) for _,x in sorted(zip(heuristics,items))]
        new_items = [x.split("$%$")[0] for x,y in search_results]
        results = []
        [results.append(x) for x in new_items if x not in results]
        print(search_results)
        print(results)
        return results
                    

if __name__ == '__main__':
    sct = ScanTables()
    sct.full_scan("Professional2")