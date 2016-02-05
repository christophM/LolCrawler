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

def surrendered(match):
    '''Checks if the match was surrendered  by one of the teams'''
    ## Improvement suggestion: Use match timeline if available
    ## Improvement: Build prediction model based on labeled matches

    match_duration = match['matchDuration']

    ## Cannot surrender before Minute 20
    if match_duration < 60 * 20:
        return 0
    ## Guess surrender by team stats
    winner_stats = list(filter(lambda x: x['winner'], match['teams']))[0]
    ## If less than 5 towers have been destroyed by winner, it is a surrender
    if winner_stats['towerKills'] < 5:
        return 1
    ## Cannot win a game without inhibitor kills
    if winner_stats['inhibitorKills'] == 0:
        return 1
    ## Matches that ended after minute 20 are more likely to be surrendered matches. Based on gut feeling.
    if (match_duration  > 60 * 20) and (match_duration < 60 * 21):
        return 0.5
    return 0.05


def surrendered_at_20(match):
    '''Checks if the match was surrendered at 20 by one of the teams'''
    match_duration = match['matchDuration']
    ended_at_20 = ((match_duration  > 60 * 20) and (match_duration < 60 * 21))
    return ended_at_20 * surrendered(match)


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
    extractions['surrendered'] = surrendered(match)
    extractions['surrenderedAt20'] = surrendered_at_20(match)
    return extractions



