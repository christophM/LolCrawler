import sys
import time
import numpy as np
from .rito import RitoAPI, NotFoundError, RateLimitExceeded, RitoServerError
from datetime import datetime
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
import pymongo
import logging
import re

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

# create a file handler

handler = logging.FileHandler('crawler.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


MATCHLIST_COLLECTION = "matchlist"
MATCH_COLLECTION = "match"


class LolCrawler():
    """Crawler that randomly downloads summoner match lists and matches"""

    def __init__(self, api, db_client, region, include_timeline=False):
        self.api = api
        self.region = region
        self.include_timeline = include_timeline
        self.summoner_ids_done = []
        self.summoner_ids = []
        self.match_ids_done = []
        self.match_ids = []
        self.db_client = db_client


    def start(self, start_summoner_id):
        """Start infinite crawling loop"""

        logger.info("Start crawling")
        last_summoner_cursor = self.db_client[MATCHLIST_COLLECTION].find({"region": self.region}).sort("$natural", pymongo.DESCENDING)
        if last_summoner_cursor.count() == 0:
            self.summoner_ids = [start_summoner_id]
            logger.info("No summoner ids found in database, starting with seed summoner")
        else:
            for i in range(0, 100):
                self.summoner_ids += [last_summoner_cursor.next()["_id"]]
            logger.info("Starting with latest summoner ids in database")
        while True:
            self.crawl()


    def _store(self, identifier, entity_type, entity, upsert=False):
        """Stores matches and matchlists"""
        entity.update({'_id': identifier})
        entity.update({'region': self.region})
        try:
            if upsert:
                self.db_client[entity_type].replace_one(filter={"_id": identifier}, replacement = entity, upsert=True)
            else:
                self.db_client[entity_type].insert_one(entity)
        except DuplicateKeyError:
            logger.info("Duplicate: Mongodb already inserted {entity_type} with id {identifier}".format(entity_type=entity_type, identifier=identifier))
        except ServerSelectionTimeoutError as e:
            logger.error("Could not reach Mongodb", exc_info=True)
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

        match = self.api.get_match(match_id=match_id, include_timeline=self.include_timeline)
        match["patch"] = match["matchVersion"][0:4]
        match["patchMajorNumeric"] = int(re.findall("([0-9]+)\.[0-9]+\.", match["matchVersion"])[0])
        match["patchMinorNumeric"] = int(re.findall("[0-9]+\.([0-9]+)\.", match["matchVersion"])[0])
        self._store(identifier=match_id, entity_type=MATCH_COLLECTION, entity=match)
        summoner_ids = [x['player']['summonerId'] for x in match['participantIdentities']]
        ## remove summoner ids the crawler has already seen
        new_summoner_ids = list(set(summoner_ids) - set(self.summoner_ids_done))
        self.summoner_ids = new_summoner_ids + self.summoner_ids


    def crawl(self):
        summoner_id = self.summoner_ids.pop()
        logger.info("Crawling summoner {summoner_id}".format(summoner_id=summoner_id))

        try:
            match_ids = self.crawl_matchlist(summoner_id)
            ## Choose from last ten matches
            random_match_id = np.random.choice(range(0, min(10, len(match_ids))))
            match_id = match_ids[random_match_id]
            self.crawl_match(match_id)
        except (NotFoundError, KeyError) as e:
            logger.exception(e)
            self.crawl()
        except (RitoServerError, RateLimitExceeded) as e:
            logger.info(e)
            logger.info("Trying again in 5 seconds")
            time.sleep(5)
            self.crawl()








