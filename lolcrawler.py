import sys
import time
import numpy as np 
from rito_api import RitoAPI
from datetime import datetime
from pymongo.errors import DuplicateKeyError


class LolCrawler():
    """Crawler that randomly downloads summoner match lists and matches"""    

    def __init__(self, api, db_client):
        self.api = api
        self.summoner_ids_done = []
        self.summoner_ids = []
        self.match_ids_done = []
        self.match_ids = []
        self.counter = 0
        self.db_client = db_client

    
    def start(self, start_summoner_id):
        """Start infinite crawling loop"""
        self.summoner_ids = [start_summoner_id]
        while True:
            self.crawl()


    def _store(self, identifier, entity_type, entity):
        """Stores matches and matchlists"""
        entity.update({'_id': identifier})
        try: 
            self.db_client[entity_type].insert_one(entity)
        except DuplicateKeyError:
            print "Duplicate: Mongodb already inserted %s with id %s" % (entity_type, identifier)


    def crawl(self):

        self.counter += 1
        summoner_id = self.summoner_ids.pop()
        print "Crawling summoner {summoner_id}".format(summoner_id=summoner_id)

        match_list = self.api.get_matchlist(summoner_id)

        self._store(identifier=summoner_id, entity_type='matchlist', entity=match_list)
        self.summoner_ids_done.append(summoner_id)

        match_ids = [x['matchId'] for x in match_list['matches']]
        self.match_ids.extend(match_ids)
        ## get random match
        random_number = np.random.choice(range(0,len(match_ids)))
        match_id = match_ids[random_number]
        match = self.api.get_match(match_id=match_id)
        self._store(identifier=match_id, entity_type='match', entity=match)

        summoner_ids = [x['player']['summonerId'] for x in match['participantIdentities']]
        ## remove summoner ids the crawler has already seen
        new_summoner_ids = list(set(summoner_ids) - set(self.summoner_ids_done))
        self.summoner_ids = self.summoner_ids + list(np.random.choice(new_summoner_ids, len(new_summoner_ids), replace=False))





