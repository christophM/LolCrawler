import re
from collections import Counter


TIER_ORDER = {"CHALLENGER": 7,
              "MASTER": 6,
              "DIAMOND": 5,
              "PLATINUM": 4,
              "GOLD": 3,
              "SILVER": 2,
              "BRONZE": 1,
              "UNRANKED": 0}

def surrendered():
    '''Checks if the match was surrendered  by one of the teams'''
    ## Check if Nexus turrets killed and position of players?
    pass

def surrendered_at_20(match):
    '''Checks if the match was surrendered at 20 by one of the teams'''
    pass


def get_highest_tier(tiers_list):
    '''Extract highest tier in tiers_list'''
    ## Filter keys that appeared in the match
    match_tiers = { key: TIER_ORDER[key] for key in tiers_list}
    highest_tier = max(match_tiers, key=match_tiers.get)
    return highest_tier


def get_lowest_tier(tiers_list):
    '''Extract the lowest tier in tiers_list'''
    match_tiers = { key: TIER_ORDER[key] for key in tiers_list}
    lowest_tier = min(match_tiers, key=match_tiers.get)
    return lowest_tier


def extract_tier(match):
    '''Extract the most common highestAchievedSeasonTier of players in match'''
    count = Counter([x["highestAchievedSeasonTier"] for x in match["participants"]])
    try:
        most_common = count.most_common()[0][0]
    except:
        most_common = "NA"
    return most_common


def extract_match_infos(match):
    """Extract additional information from the raw match data
    """
    extractions = {}
    extractions["patchMajorNumeric"] = int(re.findall("([0-9]+)\.[0-9]+\.", match["matchVersion"])[0])
    extractions["patchMinorNumeric"] = int(re.findall("[0-9]+\.([0-9]+)\.", match["matchVersion"])[0])
    extractions["patch"] = str(re.findall("([0-9]+\.[0-9]+)\.", match["matchVersion"])[0])
    extractions["tier"] = extract_tier(match)
    tiers = [x["highestAchievedSeasonTier"] for x in match["participants"]]
    extractions["highestPlayerTier"] = get_highest_tier(tiers)
    extractions["lowestPlayerTier"] = get_lowest_tier(tiers)
    return extractions



