from config import config
from pymongo import MongoClient
from clint import arguments
from datetime import datetime
from config import config
import json
import os
import requests


CHAMP_MAP_PATH="./data/champion-map.json"


def download_champion_names():
    """Uses Riot API to download the names of the champions"""
    print("Downloading champion names and storing as %s" % (CHAMP_MAP_PATH))
    api_key = config["api_key"]
    url = "https://global.api.pvp.net/api/lol/static-data/euw/v1.2/champion?api_key=%s" % (api_key)
    champs_dict = requests.get(url).json()["data"]
    my_champ_dict={}
    for key, value in champs_dict.iteritems():
        my_champ_dict.update({value["id"]: value["name"]})
    with open(CHAMP_MAP_PATH, "w") as f:
        json.dump(my_champ_dict, f)


def update_aggregates(db):
    """Aggregate matches
    - champion win counters
    - TBC
    """

    ## Only touch API if file with champ id -> name map does not exist
    if not os.path.isfile(CHAMP_MAP_PATH):
        download_champion_names()
    with open(CHAMP_MAP_PATH) as data_file:
        my_champ_dict=json.load(data_file)

    ## Create cursor over all games with non-existent champions-counted=TRUE
    ## Need snapshot to not iterate twice over the doc
    cur = db["match"].find({"extractions.postProcessedAt": {"$exists": False}},
                           modifiers={"snapshot": True})
    match_count = cur.count()
    index = 0
    print("Processing %i matches" % (match_count))

    while index != match_count:
        match = cur.next()
        matchId = match["_id"]
        db["match"].update_one({"_id": matchId},
                           {"$set": {"extractions.postProcessedAt": datetime.now()}})
        if match["matchMode"] != "CLASSIC":
            continue

        ##db["champStats"].update_many()
        index += 1

        winner_team100 = match["teams"][0]["winner"]
        for x in match["participants"]:
            ## Identifier
            identifier = {
                "region": match["region"],
                "minorPatch": match["extractions"]["patchMinorNumeric"],
                "majorPatch": match["extractions"]["patchMajorNumeric"],
                "patch": match["extractions"]["patch"],
                "matchVersion": match["matchVersion"],
                "matchType": match["matchType"],
                "queuType": match["queueType"],
                "mapId": match["mapId"],
                "role": x["timeline"]["role"],
                "lane": x["timeline"]["lane"],
                "teamId": x["teamId"],
                "championName": my_champ_dict[str(x["championId"])],
                "championId": x["championId"]
                }


            ## Has the participant won the match with this champ?
            win = 1 * ((x["teamId"] == "100")  ==  winner_team100)
            increase = {
                "victory_count": win,
                "match_count": 1,
                "defeat_count": 1 - win
            }

            db["champStats"].update_one(identifier,
                                        {"$inc": increase,
                                         "$setOnInsert": identifier},
                                        upsert=True)
    return True

def reset_aggregates(db):
    """Removes the flags in the matches and deletes the table with the aggregates
    """
    ## TODO: Optional argument for filtering specific match subset, for example the current
    ##       patchVersion
    print("Deleting aggregates and removing flags from matches")
    db["match"].update_many({"extractions.postProcessedAt": {"$exists": True}},
                       {"$unset": {"extractions.postProcessedAt": ""}},
                       upsert=False)

    db["champStats"].delete_many({})
    return True

def reprocess_aggregates(db):
    reset_aggregates(db)
    update_aggregates(db)
    return True



if __name__=="__main__":

    ## Connect to MongoDB database
    client = MongoClient(config['mongodb']['host'], config['mongodb']['port'])
    db = client[config['mongodb']['db']]

    args = arguments.Args()
    action = args.get(0)
    if action=="update":
        update_aggregates(db)
    elif action=="reset":
        reset_aggregates(db)
    elif action=="reprocess":
        reprocess_aggregates(db)
    else:
        print("Please choose either update, reset or reprocess")





