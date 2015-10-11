import sys
import time
import numpy as np
from rito_api import RitoAPI, NotFoundError, RateLimitExceeded, RitoServerError
from datetime import datetime
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
import pymongo

MATCHLIST_COLLECTION = "matchlist"
MATCH_COLLECTION = "match"


class LolCrawler():
    """Crawler that randomly downloads summoner match lists and matches"""

    def __init__(self, api, db_client):
        self.api = api
        self.summoner_ids_done = []
        self.summoner_ids = []
        self.match_ids_done = []
        self.match_ids = []
        self.db_client = db_client


    def start(self, start_summoner_id):
        """Start infinite crawling loop"""

        last_summoner_cursor = self.db_client[MATCHLIST_COLLECTION].find().sort("$natural", pymongo.DESCENDING)
        if last_summoner_cursor.count() == 0:
            self.summoner_ids = [start_summoner_id]
        else:
            self.summoner_ids = [last_summoner_cursor.next()["_id"] for x in range(0,10)]
        while True:
            self.crawl()


    def _store(self, identifier, entity_type, entity, upsert=False):
        """Stores matches and matchlists"""
        entity.update({'_id': identifier})
        try:
            if upsert:
                self.db_client[entity_type].replace_one(filter={"_id": identifier}, replacement = entity, upsert=True)
            else:
                self.db_client[entity_type].insert_one(entity)
        except DuplicateKeyError:
            print "Duplicate: Mongodb already inserted %s with id %s" % (entity_type, identifier)
        except ServerSelectionTimeoutError, e:
            print e
            print "Could not reach Mongodb"
            sys.exit(1)

    def crawl_matchlist(self, summoner_id):
        """Crawls matchlist of given summoner,
        stores it and saves the matchIds"""
        matchlist = self.api.get_matchlist(summoner_id)
        self._store(identifier=summoner_id, entity_type=MATCHLIST_COLLECTION, entity=matchlist, upsert=True)
        self.summoner_ids_done.append(summoner_id)
        match_ids = [x['matchId'] for x in matchlist['matches']]
        self.match_ids.extend(match_ids)
        return match_ids

    def crawl_match(self, match_id):
        match = self.api.get_match(match_id=match_id)
        self._store(identifier=match_id, entity_type=MATCH_COLLECTION, entity=match)
        summoner_ids = [x['player']['summonerId'] for x in match['participantIdentities']]
        ## remove summoner ids the crawler has already seen
        new_summoner_ids = list(set(summoner_ids) - set(self.summoner_ids_done))
        self.summoner_ids = self.summoner_ids + list(np.random.choice(new_summoner_ids, len(new_summoner_ids), replace=False))


    def crawl(self):

        summoner_id = self.summoner_ids.pop()
        print "Crawling summoner {summoner_id}".format(summoner_id=summoner_id)

        try:
            match_ids = self.crawl_matchlist(summoner_id)
            ## get random match
            random_number = np.random.choice(range(0,len(match_ids)))
            match_id = match_ids[random_number]
            self.crawl_match(match_id)
        except (NotFoundError, KeyError) as e:
            print e
            self.crawl()
        except (RitoServerError, RateLimitExceeded) as e:
            print e
            print "Trying again in 30 seconds"
            time.sleep(30)
            self.crawl()








