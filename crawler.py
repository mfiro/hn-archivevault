import argparse 
import sqlite3
import time
from tqdm import tqdm
from hn import Client


def insert_story(data):
    connection = sqlite3.connect('hn_archive.db')
    cursor = connection.cursor()
    
    cursor.execute('''
    INSERT or REPLACE INTO stories (id, by, score, comment_count, time, title, type, url, time_str, synced_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['id'], data['by'], data['score'], data['descendants'], data['time'], data['title'], data['type'], data.get('url'), data['time_str'], int(time.time())))
    
    connection.commit()
    connection.close()


def insert_comment(data):
    connection = sqlite3.connect('hn_archive.db')
    cursor = connection.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO comments (id, by, parent, text, time, type, time_str)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['id'], data['by'], data['parent'], data['text'], data['time'], data['type'], data['time_str']))
    
    connection.commit()
    connection.close()


def fetch_and_store_item(item_id, skip_comments=False):
    print(f"Fetching item id {item_id} ...")
    item = client.get_item(item_id)

    if item.get('deleted') or item.get('dead'):
        print(f"Skipping{item_id}: flagged as deleted ...")
    else:
        if item['type'] == 'story':
            print(f"Inserting {item_id} to stories in DB ...")
            insert_story(item)
        elif item['type'] == 'comment' and not skip_comments:
            print(f"Inserting {item_id} to comments in DB ...")
            insert_comment(item)


def get_current_max_id_from_db():
    connection = sqlite3.connect('hn_archive.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT MAX(id) FROM (SELECT id FROM stories UNION ALL SELECT id FROM comments)')
    max_id = cursor.fetchone()[0]
    connection.close()
    return max_id or 0


def update_new_items(first_run=False, skip_comments=False):
    max_id = client.get_maxitem()
    if first_run:
        # Set a more recent starting point for the first run, as the first run takes time.
        current_max_id = max_id - 1000
    else:
        current_max_id = get_current_max_id_from_db()

    # Now proceed to fetch items from current_max_id up to the max_id
    print(f"Start Fetching {max_id - current_max_id} items ...")
    for item_id in tqdm(range(current_max_id + 1, max_id + 1)):
        fetch_and_store_item(item_id, skip_comments)


def update_all_stories():
    # Get all the story ids
    connection = sqlite3.connect('hn_archive.db')
    cursor = connection.cursor()
    sql_query = 'SELECT id FROM stories'
    cursor.execute(sql_query)
    story_ids = cursor.fetchall()
    connection.close()

    # Loop over them
    for story_id in tqdm(story_ids):
        fetch_and_store_item(story_id[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Hacker News items in database.')
    parser.add_argument('--first_run', action='store_true', 
                        help='Set this flag if it is the first run to only fetch the most recent items.')
    parser.add_argument('--skip_comments', action='store_true', 
                        help="Set this flag if you don't want to store the comments in the database")
    parser.add_argument('--update_stories', action='store_true', 
                        help="Set this flag if you just want to update the story informations.")
    args = parser.parse_args()
    
    print(f"Running the crawler ...")
    client = Client()
    if args.update_stories:
        print(f"Updating stories ...")
        update_all_stories()
    else:
        update_new_items(first_run=args.first_run,
                     skip_comments=args.skip_comments)
