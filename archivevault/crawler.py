import argparse
import logging
import sqlite3
import time
from tqdm import tqdm
from hn import Client

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='crawler.log',
                    filemode='a')

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

    def __repr__(self):
         return (
             f"{self.__class__.__name__}:\n"
             f"\t db_pathname={self.db_pathname!r}\n"
             f"\t first_run={self.first_run!r}\n"
             f"\t test_mode={self.test_mode!r}")

    def insert_story(self, data):
        try:
            self.cursor.execute('''
            INSERT or REPLACE INTO stories (id, by, score, comment_count, time, title, type, url, time_str, synced_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['id'], data['by'], data['score'], data['descendants'], data['time'], data['title'], data['type'], data.get('url'), data['time_str'], int(time.time())))
            
            self.connection.commit()
        except Exception as e:
            logging.error(f"Failed to insert story {data['id']}: {e}")

    def insert_comment(self, data):  
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO comments (id, by, parent, text, time, type, time_str)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['id'], data['by'], data['parent'], data['text'], data['time'], data['type'], data['time_str']))
            
            self.connection.commit()
        except Exception as e:   
            logging.error(f"Failed to insert comment {data['id']}: {e}")

    def fetch_and_store_item(self, item_id):
        logging.info(f"Fetching item id {item_id} ...")
        item = self.hn_client.get_item(item_id)

        if item.get('deleted') or item.get('dead'):
            logging.info(f"Skipping{item_id}: flagged as deleted or dead.")
            return
        else:
            if item['type'] == 'story':
                logging.info(f"Inserting {item_id} to stories in DB ...")
                self.insert_story(item)
            elif item['type'] == 'comment' and not self.skip_comments:
                logging.info(f"Inserting {item_id} to comments in DB ...")
                self.insert_comment(item)

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
        logging.info(f"Start Fetching {max_id - current_max_id} items ...")
        for item_id in tqdm(range(current_max_id + 1, max_id + 1)):
            self.fetch_and_store_item(item_id)

    def get_current_max_id_from_db(self):
        try:
            self.cursor.execute('SELECT MAX(id) FROM (SELECT id FROM stories UNION ALL SELECT id FROM comments)')
            max_id = self.cursor.fetchone()[0]
            return max_id or 0
        except Exception as e:
            logging.error(f"Failed to get current max ID from DB: {e}")
            return 0

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
    
    logging.info(f"Running the crawler ...")

    # Initialising API client
    client = Client()

    # Initialising the Crawler
    crawler = Crawler(hn_client=client,
                      first_run=args.first_run, 
                      skip_comments=args.skip_comments)

    if args.update_stories:
        logging.info(f"Updating stories ...")
        crawler.update_all_stories()
    else:
        logging.info(f"Fetching new items ...")
        crawler.fetch_new_items()
