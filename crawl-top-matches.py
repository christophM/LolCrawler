from config import config
from pymongo import MongoClient
from lolcrawler.lolcrawler import TopLolCrawler
from datetime import datetime
from riotwatcher import RateLimit, RiotWatcher, LoLException

SEASON="SEASON2016"
REGION="na"




## Connect to MongoDB database
client = MongoClient(config['mongodb']['host'], config['mongodb']['port'])
db = client[config['mongodb']['db']]

## Initialise Riot API wrapper
rate_limits = limits=(RateLimit(3000,10), RateLimit(180000,600))
api_key = config['api_key']

if api_key=='':
    raise LookupError("Provide your API key in config.py")

api = RiotWatcher(config['api_key'], limits = rate_limits, default_region='euw')
summoner_id = '32450058'
match = api.get_match_list(summoner_id=summoner_id)



crawler = TopLolCrawler(api,db_client=db)




crawler.start(begin_time=datetime(2016, 1, 1),
              regions=['euw', 'na', 'eune', 'kr'])



