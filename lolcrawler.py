import sys
import time
import numpy as np 
import json
from rito_api import RitoAPI
from datetime import datetime



class LolCrawler():
    """Crawler that randomly downloads summoner match histories and matches"""    

    def __init__(self, api, get_complete_matchhistory):
        self.api = api
        self.summoner_ids_done = []
        self.summoner_ids = []
        self.match_ids_done = []
        self.match_ids = []
        self.counter = 0
        self.get_complete_matchhistory = get_complete_matchhistory

    
    def start(self, start_summoner_id,  n_requests=1000):
        """Start infinite crawling loop"""
        self.summoner_ids = [start_summoner_id]
        while self.counter < n_requests:
            self.crawl()

    def _store(self, file_url, entity_json):
        f = open(file_url,'w')
        f.write(entity_json)
        f.close() 

    def store_match_history(self, match_history, summoner_id):
        match_history_json = json.dumps(match_history)
        file_url = './matchhistories/{summoner_id}.json'.format(summoner_id=summoner_id)
        self._store(file_url, match_history_json)

    def store_match(self, match, match_id):
        match_json = json.dumps(match)
        file_url = './matches/{match_id}.json'.format(match_id=match_id)
        self._store(file_url, match_json)

    def crawl(self):
        self.counter += 1
        summoner_id = self.summoner_ids.pop()
        print "Crawling summoner {summoner_id}".format(summoner_id=summoner_id)

        try:
            if self.get_complete_matchhistory:
                match_history = self.api.get_complete_matchhistory(summoner_id)
            else:
                match_history = self.api.get_matchhistory(summoner_id)["matches"]
            self.store_match_history(match_history, summoner_id)
            self.summoner_ids_done.append(summoner_id)
            match_ids = [x['matchId'] for x in match_history]
            self.match_ids.extend(match_ids)
            ## get random match
            random_number = np.random.choice(range(0,len(match_ids)))
            match_id = match_ids[random_number]
        except: 
            print "Failed to download and store match history"

        try:
            match = self.api.get_match(match_id=match_id)
            self.store_match(match, match_id)
            summoner_ids = [x['player']['summonerId'] for x in match['participantIdentities']]
            ## remove summoner ids the crawler has already seen
            new_summoner_ids = list(set(summoner_ids) - set(self.summoner_ids_done))
            self.summoner_ids = self.summoner_ids + list(np.random.choice(new_summoner_ids, len(new_summoner_ids), replace=False))
        except:
            print "Failed to download and store match"





