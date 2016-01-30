import sys
import time
import numpy as np
from .rito import RitoAPI, NotFoundError, RateLimitExceeded, RitoServerError
from datetime import datetime
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
import pymongo
import logging
import re
from collections import Counter

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
MATCHLIST_PAGE_LIMIT = 60


## TODO: Crawling of RANKED_TEAM_5x5 in ChallengerLolCrawler
## TODO: Add looping through regions
## TODO: Make it possible to provide leagues as list
## TODO: Regions as argument to crawl()
## TODO: seasons as argument to crawl()
## TODO: Add logging
## TODO: Implement highestTier as extractions for match
## TODO: Extend crawl.py script with new Crawler
## TODO:
## TODO: Maybe create a method in rito.py to have the pagination and MATCHLIST_PAGE_LIMIT
##       in the API logic
## TODO: Remove crawl-top-matches.py again
## TODO: Implement startDate for matchlist to avoid getting too many games.


class LolCrawlerBase():
    """Crawler base class for all crawlers"""

    def __init__(self, api, db_client, region, include_timeline=False):
        self.api = api
        self.region = region
        self.include_timeline = include_timeline
        self.summoner_ids_done = []
        self.summoner_ids = []
        self.match_ids_done = []
        self.match_ids = []
        self.db_client = db_client


    def _store(self, identifier, entity_type, entity, upsert=False):
        """Stores matches and matchlists"""
        entity.update({'_id': identifier})
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
        matchlist["extractions"] = {"region": self.region}
        self._store(identifier=summoner_id, entity_type=MATCHLIST_COLLECTION, entity=matchlist, upsert=True)
        self.summoner_ids_done.append(summoner_id)
        match_ids = [x['matchId'] for x in matchlist['matches']]
        self.match_ids.extend(match_ids)
        return match_ids

    def crawl_complete_matchlist(self, summoner_id, params={}):
        """Crawls complete matchlist by going through paginated matchlists of given summoner,
        stores it and saves the matchIds"""
        more_matches=True
        ## Start with empty matchlist
        matchlist={"matches": [], "totalGames": 0}
        begin_index=0
        while more_matches:
            params.update({"beginIndex": begin_index, "endIndex": begin_index + MATCHLIST_PAGE_LIMIT})
            new_matchlist = self.api.get_matchlist(summoner_id=summoner_id, params=params)
            if "matches" in new_matchlist.keys():
                matchlist["matches"] = matchlist["matches"] + new_matchlist["matches"]
                matchlist["totalGames"] = matchlist["totalGames"] + new_matchlist["totalGames"]
                begin_index += MATCHLIST_PAGE_LIMIT
            else:
                more_matches=False
        matchlist["extractions"] = {"region": self.region}
        self._store(identifier=summoner_id, entity_type=MATCHLIST_COLLECTION, entity=matchlist, upsert=True)
        self.summoner_ids_done.append(summoner_id)
        match_ids = [x['matchId'] for x in matchlist['matches']]
        self.match_ids.extend(match_ids)
        return match_ids


    def crawl_match(self, match_id):
        """Crawl match with given match_id,
        stores it and saves the matchID"""
        ## Check if match is in database and only crawl if not in database
        match_in_db = self.db_client[MATCH_COLLECTION].find({"_id": match_id})
        if match_in_db.count() == 0:
            match = self.api.get_match(match_id=match_id, include_timeline=self.include_timeline)
            match["extractions"] = extract_match_infos(match)
            self._store(identifier=match_id, entity_type=MATCH_COLLECTION, entity=match)
            summoner_ids = [x['player']['summonerId'] for x in match['participantIdentities']]
            ## remove summoner ids the crawler has already seen
            new_summoner_ids = list(set(summoner_ids) - set(self.summoner_ids_done))
            self.summoner_ids = new_summoner_ids + self.summoner_ids





class LolCrawler(LolCrawlerBase):
    """Randomly crawls matches starting from seed summoner"""

    def start(self, start_summoner_id):
        """Start infinite crawling loop"""
        logger.info("Start crawling")
        last_summoner_cursor = self.db_client[MATCHLIST_COLLECTION].find({"extractions.region": self.region}).sort("$natural", pymongo.DESCENDING)
        if last_summoner_cursor.count() == 0:
            self.summoner_ids = [start_summoner_id]
            logger.info("No summoner ids found in database, starting with seed summoner")
        else:
            for i in range(0, 100):
                self.summoner_ids += [last_summoner_cursor.next()["_id"]]
            logger.info("Starting with latest summoner ids in database")
        while True:
            self.crawl()


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



class ChallengerLolCrawler(LolCrawler):
    """Crawl all matches from all challengers"""


    def crawl(self, league="challenger", season="SEASON2016"):
        ## Crawl all regions. But start with initialised one for now.
        ## Step 1 a): Crawling league for summoner_ids (solo q)
        ## Step 1 b): Crawling league for team ids (team q)
        ## Step 1 c): Turning team ids into summoner ids
        ## Step 2: Crawling summoner_ids for matchlists
        ## Step 3: Crawling match_ids from matchlists for matches
        ## Second step is the crawling of match_ids based on the matchlists
        queue = "RANKED_SOLO_5x5"
        league_list = self.api.get_league(league=league, queue=queue)
        self.summoner_ids = [x["playerOrTeamId"] for x in league_list["entries"]]
        for summoner_id in self.summoner_ids:
            print("Crawling ", summoner_id)
            try:
                self.crawl_complete_matchlist(summoner_id, params={"seasons": season, "rankedQueues": queue})
            except (NotFoundError, KeyError) as e:
                logger.exception(e)
                self.crawl()
            except (RitoServerError, RateLimitExceeded) as e:
                logger.info(e)
                time.sleep(5)

        for match_id in self.match_ids:
            print match_id
            ## TODO: Add try except
            try:
                self.crawl_match(match_id)
            except (NotFoundError, KeyError) as e:
                logger.exception(e)
                self.crawl()
            except (RitoServerError, RateLimitExceeded) as e:
                logger.info(e)
                time.sleep(5)
        return True





def extract_match_infos(match):
    """Extract additional information from the raw match data
    """
    extractions = {}
    extractions["patchMajorNumeric"] = int(re.findall("([0-9]+)\.[0-9]+\.", match["matchVersion"])[0])
    extractions["patchMinorNumeric"] = int(re.findall("[0-9]+\.([0-9]+)\.", match["matchVersion"])[0])
    extractions["patch"] = str(re.findall("([0-9]+\.[0-9]+)\.", match["matchVersion"])[0])
    extractions["tier"] = extract_tier(match)
    return extractions


def extract_tier(match):
    count = Counter([x["highestAchievedSeasonTier"] for x in match["participants"]])
    ## del count["UNRANKED"]
    try:
        most_common = count.most_common()[0][0]
    except:
        most_common = "NA"
    return most_common


