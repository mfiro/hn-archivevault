import argparse 
import sqlite3
import time
from tqdm import tqdm
from hn import Client


class Crawler:
    def __init__(self,
                hn_client,
                db_pathname='hn_archive.db',
                first_run=False,
                skip_comments=False,
                test_mode=False,
                ):
        self.db_pathname = db_pathname
        self.first_run = first_run
        self.skip_comments = skip_comments
        self.test_mode = test_mode
        self.hn_client = hn_client
        self.connection = sqlite3.connect(self.db_pathname)
        self.cursor = self.connection.cursor()
    
    def __del__(self):
        self.connection.close()

    def insert_story(self, data):
        self.cursor.execute('''
        INSERT or REPLACE INTO stories (id, by, score, comment_count, time, title, type, url, time_str, synced_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['id'], data['by'], data['score'], data['descendants'], data['time'], data['title'], data['type'], data.get('url'), data['time_str'], int(time.time())))
        
        self.connection.commit()

    def insert_comment(self, data):       
        self.cursor.execute('''
        INSERT OR REPLACE INTO comments (id, by, parent, text, time, type, time_str)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['id'], data['by'], data['parent'], data['text'], data['time'], data['type'], data['time_str']))
        
        self.connection.commit()

    def fetch_and_store_item(self, item_id):
        print(f"Fetching item id {item_id} ...")
        item = self.hn_client.get_item(item_id)

        if item.get('deleted') or item.get('dead'):
            print(f"Skipping{item_id}: flagged as deleted ...")
        else:
            if item['type'] == 'story':
                print(f"Inserting {item_id} to stories in DB ...")
                self.insert_story(item)
            elif item['type'] == 'comment' and not self.skip_comments:
                print(f"Inserting {item_id} to comments in DB ...")
                self.insert_comment(item)

    def get_current_max_id_from_db(self):
        self.cursor.execute('SELECT MAX(id) FROM (SELECT id FROM stories UNION ALL SELECT id FROM comments)')
        max_id = self.cursor.fetchone()[0]
        return max_id or 0

    def fetch_new_items(self):
        max_id = self.hn_client.get_maxitem()
        if self.first_run:
            # Set a more recent starting point for the first run, as the first run takes time.
            current_max_id = max_id - 1000
        else:
            current_max_id = self.get_current_max_id_from_db()
        
        if self.test_mode:
            max_id = current_max_id+5

        # Now proceed to fetch items from current_max_id up to the max_id
        print(f"Start Fetching {max_id - current_max_id} items ...")
        for item_id in tqdm(range(current_max_id + 1, max_id + 1)):
            self.fetch_and_store_item(item_id)

    def update_all_stories(self):
        # Get all the story ids
        sql_query = 'SELECT id FROM stories'
        self.cursor.execute(sql_query)
        story_ids = self.cursor.fetchall()

        if self.test_mode:
            story_ids = story_ids[:4]

        # Loop over them
        for story_id in tqdm(story_ids):
            self.fetch_and_store_item(story_id[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Hacker News items in database.')
    parser.add_argument('--first_run',
                        action='store_true', 
                        help='Set this flag if it is the first run to only fetch the most recent items.')
    parser.add_argument('--skip_comments',
                        action='store_true', 
                        help="Set this flag if you don't want to store the comments in the database")
    parser.add_argument('--update_stories',
                        action='store_true', 
                        help="Set this flag if you just want to update the story informations.")
    args = parser.parse_args()
    
    print(f"Running the crawler ...")

    # Initialising API client
    client = Client()

    # Initialising the Crawler
    crawler = Crawler(hn_client=client,
                      first_run=args.first_run, 
                      skip_comments=args.skip_comments)

    if args.update_stories:
        print(f"Updating stories ...")
        crawler.update_all_stories()
    else:
        crawler.fetch_new_items()
