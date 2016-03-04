from lolcrawler import extract_match
import json


with open('data/match_1.json') as data_file:
    ## Match with baron win, EUW
    match_1 = json.load(data_file)

with open('data/match_2.json') as data_file:
    ##
    match_2 = json.load(data_file)


short_match = {'matchDuration': 15 * 60}

four_tower_match = {'matchDuration': 25 * 60,
                    'teams': [
                        {'winner': True,
                         'towerKills': 4},
                        {'winner': False,
                         'towerKills': 6}
                         ]}

no_inhibitors_match = {'matchDuration': 25 * 60,
                    'teams': [
                        {'winner': False,
                         'towerKills': 4,
                        'inhibitorKills': 1},
                        {'winner': True,
                         'towerKills': 6,
                        'inhibitorKills': 0}
                         ]}

no_surrender_match = {'matchDuration': 25 * 60,
                    'teams': [
                        {'winner': False,
                         'towerKills': 5,
                        'inhibitorKills': 1},
                        {'winner': True,
                         'towerKills': 6,
                        'inhibitorKills': 1}
                         ]}
surrender_match = no_inhibitors_match
surrender_match.update({'matchDuration': 20.05 * 60})



## test surrendered with example match data
def test_not_surrendered_short_match():
    assert extract_match.surrendered(short_match) == 0

def test_surrendered_low_towers():
    assert extract_match.surrendered(four_tower_match) == 1

def test_surrendered_no_inhibitors():
    assert extract_match.surrendered(no_inhibitors_match) == 1

def test_no_surrender():
    assert extract_match.surrendered(no_surrender_match) == 0.05

def test_no_surrender_at_20():
    assert extract_match.surrendered_at_20(no_surrender_match) == 0

def test_surrender_at_20():
    assert extract_match.surrendered_at_20(surrender_match) == 1


tiers_list = ['CHALLENGER', 'DIAMOND', 'MASTER',
              'MASTER', 'MASTER', 'MASTER',
              'CHALLENGER', 'MASTER', 'CHALLENGER',
              'GOLD']

def test_highest_tier():
    assert extract_match.get_highest_tier(tiers_list) == 'CHALLENGER'


def test_get_lowest_tier():
    assert extract_match.get_lowest_tier(tiers_list) == 'GOLD'


def test_get_tier():
    assert extract_match.get_most_common_tier(tiers_list) == 'MASTER'




def test_patch():
    assert extract_match.extract_patch('6.1.123.93') == '6.1'


def test_patch2():
    assert extract_match.extract_patch('5.24.123.93') == '5.24'


def test_major_patch():
    assert extract_match.extract_major_patch('6.1.123.93') == 6


def test_minor_patch():
    assert extract_match.extract_minor_patch('6.1.123.93') == 1

def test_minor_patch2():
    assert extract_match.extract_minor_patch('5.24.123.93') == 24


def test_baron_win_true():
    assert extract_match.win_while_baron_buff(match_1) == True

def test_baron_win_false():
    assert extract_match.win_while_baron_buff(match_2) == False
