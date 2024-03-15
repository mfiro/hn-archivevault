# hn-archivevault

**hn-archivevault** is a Python-based project aimed at archiving stories and comments from Hacker News. This project uses sqlite3 for database management and a custom library [hnconnector](https://github.com/mfiro/hnconnector)  to interact with the Hacker News API. It is designed to allow for both initial data capture and periodic updates to the archive.

## Project Scope
This github project is designed solely for the purpose of coding practice and exploration of data from Hacker News. It allows users to archive stories and comments for personal use or development purposes. Please note, this project is code-based and does not intend to publish the archived database publicly. It serves as a foundation for creating new UIs or for personal exploration of Hacker News data trends over time.

## Getting Started
### Cloning the project
```bash
git clone https://github.com//hn-archivevault.git
cd hn-archivevault
```

### Installing required packages (prefereably in your desired virtual environment)
```bash
pip install -r requirements.txt
```

### Setting Up the Database
To initialize the database, run:
```bash
python initial_db_setup.py
```
This will creates the sqlite3 file **hn_archive.db** and two tables in it: stories and comments.

### Running the Crawler
To start the archiving process for the first time, run:
```bash
python crawler.py --first_run
```
For subsequent updates to the archive just omit flag:
```bash
python crawler.py
```


## Author
[https://github.com/mfiro](https://github.com/mfiro)

## Appreciation for Open APIs
In an era where many social media platforms have closed off or discontinued their public APIs, I extend my sincere appreciation to Hacker News for maintaining open access to their data. This openness is invaluable for developers, researchers, and enthusiasts who wish to create tools, 3rd party application and UIs, conduct analyses, or simply explore data in innovative ways. I believe Open data policies significantly contribute to the richness of the internet ecosystem, fostering creativity, transparency, and community engagement.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details




