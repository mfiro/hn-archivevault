import argparse 
import sqlite3
from tqdm import tqdm
from helpers import load_json, save_json
from hn import Client


def insert_story(data):
    connection = sqlite3.connect('hn_archive.db')
    cursor = connection.cursor()
    
    cursor.execute('''
    INSERT or REPLACE INTO stories (id, by, score, time, title, type, url, time_str)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['id'], data['by'], data['score'], data['time'], data['title'], data['type'], data.get('url'), data['time_str']))
    
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


def fetch_and_store_item(item_id):
    print(f"Fetching item id {item_id} ...")
    item = client.get_item(item_id)

    if item.get('deleted') or item.get('dead'):
        print(f"Skipping{item_id}: flagged as deleted ...")
    else:
        if item['type'] == 'story':
            print(f"Inserting {item_id} to stories in DB ...")
            insert_story(item)
        elif item['type'] == 'comment':
            print(f"Inserting {item_id} to comments in DB ...")
            insert_comment(item)


def get_current_max_id_from_db():
    connection = sqlite3.connect('hn_archive.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT MAX(id) FROM (SELECT id FROM stories UNION ALL SELECT id FROM comments)')
    max_id = cursor.fetchone()[0]
    connection.close()
    return max_id or 0


def update_new_items(first_run=False):
    max_id = client.get_maxitem()
    if first_run:
        # Set a more recent starting point for the first run, as the first run takes time.
        current_max_id = max_id - 1000
    else:
        current_max_id = get_current_max_id_from_db()

    # Now proceed to fetch items from current_max_id up to the max_id
    print(f"Start Fetching {max_id - current_max_id} items ...")
    for item_id in tqdm(range(current_max_id + 1, max_id + 1)):
        fetch_and_store_item(item_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Hacker News items in database.')
    parser.add_argument('--first_run', action='store_true', 
                        help='Set this flag if it is the first run to only fetch the most recent items.')
    args = parser.parse_args()
    
    print(f"Running the crawler ...")
    client = Client()
    update_new_items(first_run=args.first_run)
    #fetch_and_store_item(39720909)