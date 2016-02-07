from config import config
from pymongo import MongoClient
from clint import arguments
from datetime import datetime
from config import config
import json
import os
import requests
from lolcrawler.extract_match import extract_match_infos

def extract(db):
    '''Runs extractions for all matches without extractions in the database'''
    cur = db["match"].find({"extractions": {"$exists": False}},
                           modifiers={"snapshot": True})
    match_count = cur.count()
    index = 0
    print("Processing %i matches" % (match_count))

    while index != match_count:
        match = cur.next()
        matchId = match["_id"]
        extractions = extract_match_infos(match)
        ## TODO: Add extractionsDate
        db["match"].update_one({"_id": matchId},
                              {"$set": {"extractions": extractions,
                                        "processedAt.extract": datetime.now()}})
        index += 1
    return None

def reset_extractions(db):
    '''Removes all extractions from the database'''
    ## TODO: Include projection for cursor to make process faster
    print("Deleting extractions from matches")
    db["match"].update_many({"extractions": {"$exists": True}},
                       {"$unset": {"extractions": ""}},
                       upsert=False)

    return None

if __name__=="__main__":

    ## Connect to MongoDB database
    client = MongoClient(config['mongodb']['host'], config['mongodb']['port'])
    db = client[config['mongodb']['db']]

    args = arguments.Args()
    action = args.get(0)
    if action=="reset":
        reset_extractions(db)
    elif action=='extract':
        extract(db)
    else:
        print("Please choose either extract or reset")





