from lolcrawler.rito import RitoAPI
from config import config
from pymongo import MongoClient
from lolcrawler.lolcrawler import ChallengerLolCrawler


SEASON="SEASON2016"
REGION="na"




## Connect to MongoDB database
client = MongoClient(config['mongodb']['host'], config['mongodb']['port'])
db = client[config['mongodb']['db']]

## Initialise Riot API wrapper
time_between_requests = config['rate_limit']['seconds'] / float(config['rate_limit']['n_requests'])
api_key = config['api_key']

if api_key=='':
    raise LookupError("Provide your API key in config.py")

api = RitoAPI(config['api_key'], time_between_requests, region=REGION)



crawler = ChallengerLolCrawler(api, db_client=db, region=REGION, include_timeline=True)
crawler.crawl()
