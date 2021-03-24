from .user_database import UserDatabase
from .content_database import ContentDatabase
from datetime import datetime, timedelta
import math

class ScanTables:

    def __init__(self):
        self.u_db = UserDatabase()
        self.c_db = ContentDatabase()
        self.user_scan_items = ['name', 'username', 'country', 'specialty']
        self.content_scan_items = ['title']
        self.max_distance_const = 20

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
        search_tag = search_tag.upper()
        database_item = database_item.upper()
        search_len = len(search_tag)
        database_len = len(database_item)
        search_chars = [char for char in search_tag]
        database_chars = [char for char in database_item]
        
        if search_len > database_len:
            return self.edit_distance(search_chars, database_chars, search_len, database_len)
        else:
            return self.common_substring(search_tag, database_item, search_len, database_len) + self.edit_distance(search_chars, database_chars, search_len, database_len)

    def max_edit_distance(self, search_tag, item):
        comparison_value = self.compareItems(search_tag, item)
        return comparison_value <= self.max_distance_const, comparison_value

    def filter_users(self, scan_filters, scan_items):
        new_scan_items = []
        for user in scan_items:
            isGood = False
            for key, filter_items in scan_filters.items():
                for filter_item in filter_items:
                    if user[key].upper() == filter_item.upper():
                        isGood = True
                        break
                if isGood:
                    new_scan_items.append(user)
        return new_scan_items

    def search_users(self, search_tag, scan_filters) -> (list, list):
        print(scan_filters)
        items = list()
        heuristics = list()
        scan_items = self.u_db.scan_fps()
        all_empty = True
        for key, filter_items in scan_filters.items():
            all_empty = all_empty if len(filter_items) == 0 else False
        if not all_empty:
            scan_items = self.filter_users(scan_filters, scan_items)
        for user in scan_items:
            user_email = user['email']
            for category in self.user_scan_items:
                if category == 'name':
                    user_name = user['first_name'] + " " + user['last_name']
                    isGood, heuristic_value = self.max_edit_distance(search_tag, user_name)
                    if isGood:
                        items.append(user_email + "$%$" + user_name)
                        heuristics.append(heuristic_value)
                elif category == 'country':
                    if 'country' in user:
                        if 'name' in user['country']:
                            isGood, heuristic_value = self.max_edit_distance(search_tag, user['country']['name'])
                            if isGood:
                                items.append(user_email + "$%$" + user['country']['name'])
                                heuristics.append(heuristic_value)
                elif category == 'specialty':
                    if 'specialty' in user:
                        isGood, heuristic_value = self.max_edit_distance(search_tag, user['specialty'])
                        if isGood:
                            items.append(user_email + "$%$" + user['specialty'])
                            heuristics.append(heuristic_value)
                else:
                    isGood, heuristic_value = self.max_edit_distance(search_tag, user[category])
                    if isGood:
                        items.append(user_email + "$%$" + user[category])
                        heuristics.append(heuristic_value)
        return items, heuristics

    def filter_content(self, scan_filters, scan_items):
        new_scan_items = []
        for content_item in scan_items:
            isGood = False
            content = content_item['content']
            for key, filter_items in scan_filters.items():
                for filter_item in filter_items:
                    if key == 'date':
                        print
                        past = datetime.strptime(content[key], "%m/%d/%Y")
                        present = datetime.now()
                        if filter_item == 'today' and (present - timedelta(days=1)) <= past:
                            isGood = True
                            break
                        elif filter_item == 'week' and (present - timedelta(days=7)) <= past:
                            isGood = True
                            break
                        elif filter_item == 'month' and (present - timedelta(days=30)) <= past:
                            isGood = True
                            break
                        elif filter_item == 'year' and (present - timedelta(days=365)) <= past:
                            isGood = True
                            break
                    if content[key].upper() == filter_item.upper():
                        isGood = True
                        break
                if isGood:
                    new_scan_items.append(content_item)
        return new_scan_items

    def search_content(self, search_tag, scan_filters):
        print(scan_filters)
        items = list()
        heuristics = list()
        scan_items = self.c_db.scan_content()
        all_empty = True
        for key, filter_items in scan_filters.items():
            all_empty = all_empty if len(filter_items) == 0 else False
        if not all_empty:
            scan_items = self.filter_content(scan_filters, scan_items)
        for content in scan_items:
            content_id = content['content_id']
            content_items = content['content']
            for category in self.content_scan_items:
                isGood, heuristic_value = self.max_edit_distance(search_tag, content_items[category])
                if isGood:
                    items.append(content_id+ "$%$" + content_items[category])
                    heuristics.append(heuristic_value)
        return items, heuristics


    def full_scan(self, search_tag, user_filters, content_filters):
        items = list()
        heuristics = list()
        if user_filters:
            temp_items, temp_heuristics = self.search_users(search_tag, user_filters)
            items.extend(temp_items)
            heuristics.extend(temp_heuristics)
        if content_filters:
            temp_items, temp_heuristics = self.search_content(search_tag, content_filters)
            items.extend(temp_items)
            heuristics.extend(temp_heuristics)
        search_results = [(x,_) for _,x in sorted(zip(heuristics,items))]
        new_items = [x.split("$%$")[0] for x,y in search_results]
        results = list()
        [results.append(x) for x in new_items if x not in results]
        return results
                    