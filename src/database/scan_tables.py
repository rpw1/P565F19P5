from .user_database import UserDatabase
from .content_database import ContentDatabase
import math

class ScanTables:

    def __init__(self):
        self.u_db = UserDatabase()
        self.c_db = ContentDatabase()
        self.user_scan_items = ['first_name', 'last_name', 'username', 'location', 'specialties', 'gender']
        self.content_scan_items = ['mode_of_instruction', 'workout_type', 'date', 'title']

    def edit_distance(self, search_chars, database_chars, search_len, database_len):
        board = [[0 for x in range(database_len + 1)] for x in range(search_len + 1)]
        for row in range(search_len + 1):
            for col in range(database_len + 1):
                if row == 0:
                    board[row][col] = col
                elif col == 0:
                    board[row][col] = row
                elif search_chars[row - 1] == database_chars[col - 1]:
                    board[row][col] = board[row - 1][col - 1]
                else:
                    board[row][col] = 1 + min(board[row - 1][col - 1], board[row - 1][col], board[row][col - 1])
        return board[search_len][database_len]
        

    def common_substring(self, search_tag, database_item, search_len, database_len):
        for x in range(database_len - search_len + 1):
            if database_item[x:search_len + x] == search_tag:
                return - 100
        return 0

    def compareItems(self, search_tag, database_item):
        search_len = len(search_tag)
        database_len = len(database_item)
        search_chars = [char for char in search_tag.upper()]
        database_chars = [char for char in database_item.upper()]
        if search_len > database_len:
            return self.edit_distance(search_chars, database_chars, search_len, database_len)
        else:
            return self.common_substring(search_tag, database_item, search_len, database_len) + self.edit_distance(search_chars, database_chars, search_len, database_len)

    def full_scan(self, search_tag):
        items = []
        heuristics = []
        search_dict = dict()
        for user in self.u_db.scan_users():
            user_email = user['email']
            for category in self.user_scan_items:
                if category == 'specialties':
                    for specialty in user[category]:
                        items.append(specialty)
                        heuristics.append(self.compareItems(search_tag, specialty))
                else:
                    items.append(user_email + "$%$" + user[category])
                    heuristics.append(self.compareItems(search_tag, user[category]))
        for content in self.c_db.scan_content():
            content_id = content['content_id']
            content_items = content['content']
            for category in self.content_scan_items:
                items.append(content_id + "$%$" + content_items[category])
                heuristics.append(self.compareItems(search_tag, content_items[category]))
        search_results = [(x,_) for _,x in sorted(zip(heuristics,items))]
        new_items = [x.split("$%$")[0] for x,y in search_results]
        results = []
        [results.append(x) for x in new_items if x not in results]
        print(search_results)
        print(results)
        return results
                    

if __name__ == '__main__':
    sct = ScanTables()
    sct.full_scan("Will's")