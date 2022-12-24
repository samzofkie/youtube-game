import os
from random import randint, choice, random
import re
import urllib.request
from time import sleep
from sqlalchemy import create_engine, text


class SearchTermGenerator():
    def __init__(self):
        self.cwd = os.getcwd()
        self.words = self.read_in_text_file(
                self.cwd + "/data/english_words.txt" )
        self.names = self.read_in_text_file(
                self.cwd + "/data/names.txt" )
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890'
        self.count = 0

    def read_in_text_file(self, file_path):
        lines = []
        with open(file_path, 'r') as f:
            for line in f.readlines():
                lines.append(line.split('\n')[0])
        return lines

    def get_term(self):
        if self.count == 0:
            term = self.gibberish()
        elif self.count == 1:
            term = self.name_chunk()
        else:
            term = self.word_chunk()
        self.count = 0 if self.count==2 else self.count+1
        term.replace(" ", "+")
        return term

    def gibberish(self):
        term = ''
        for i in range(randint(3,6)):
            term += choice(self.alphabet)
        return term

    def name_chunk(self):
        term = choice(self.names)
        length = len(term)
        if length > 5:
            new_length = randint(5, length-1)
            new_start = randint(0, new_length)
            return term[new_start:new_start+new_length]
        return term

    def word_chunk(self):
        term = choice(self.words)
        length = len(term)
        if length > 5:
            new_length = randint(5, length-1)
            new_start = randint(0, new_length)
            return term[new_start:new_start+new_length]
        return term


class Scraper:
    def __init__(self):
        self.term_generator = SearchTermGenerator()
        self.search_url = 'https://www.youtube.com/results?search_query='
        self.engine = create_engine( os.environ['POSTGRES_URI'], 
                                    echo=True, future=True)

    def get_term(self):
        return self.term_generator.get_term()

    def get_page(self, term):
        try:
            html = urllib.request.urlopen(self.search_url + term).read()
        except:
            return self.get_page(self.get_term())
        return html

    def extract_vid_ids(self, html):
        video_ids = re.findall(r'watch\?v=[a-zA-Z0-9_]{11}', str(html))
        video_ids = list(set(video_ids))
        video_ids = [ vid.split('watch?v=')[-1] for vid in video_ids ]
        return video_ids

    def insert_video_id(self, video_id):
        with self.engine.connect() as conn:
            conn.execute( text("INSERT INTO videos \
                      VALUES ('{}');".format(video_id)) )
            conn.commit()

    def scrape(self):
        while(1):
            term = self.get_term()
            html = self.get_page( term )
            ids = self.extract_vid_ids( html )
            if ids == []:
                print("{} ~> nada".format(term))
                continue
            vid_id = choice(ids)
            self.insert_video_id( vid_id )
            print("{} ~> {}".format(term, vid_id))
            sleep( 4 + random() * 4)
