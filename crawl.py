from lolcrawler.lolcrawler import LolCrawler
from riotwatcher import RiotWatcher, RateLimit
from config import config
from pymongo import MongoClient


if __name__=="__main__":

    ## Connect to MongoDB database
    client = MongoClient(config['mongodb']['host'], config['mongodb']['port'])
    db = client[config['mongodb']['db']]

    ## Initialise Riot API wrapper
    api_key = config['api_key']
    if api_key=='':
        raise LookupError("Provide your API key in config.py")

    region=config["region"]

    if config['is_production_key']:
        limits = (RateLimit(3000,10), RateLimit(180000,600), )
    else:
        limits = (RateLimit(10, 10), RateLimit(500, 600), )

    api = RiotWatcher(config['api_key'], default_region=region, limits=limits)

    ## Initialise crawler
    crawler =  LolCrawler(api, db_client=db, include_timeline=config["include_timeline"])

    crawler.start(config['summoner_seed_id'])


