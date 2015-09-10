from lolcrawler import LolCrawler
from rito_api import RitoAPI
from config import config
from pymongo import MongoClient


if __name__=="__main__":

    ## Connect to MongoDB database
    client = MongoClient(config['mongodb']['host'], config['mongodb']['port'])
    db = client[config['mongodb']['db']]
    
    ## Initialise Riot API wrapper
    time_between_requests = config['rate_limit']['seconds'] / float(config['rate_limit']['n_requests'])
    api_key = config['api_key']
    if api_key=='':
        raise LookupError("Provide your API key in config.py")
    api = RitoAPI(config['api_key'], time_between_requests)

    ## Initialise crawler
    crawler =  LolCrawler(api, get_complete_matchhistory=config['get_complete_matchhistory'], db_client=db)

    crawler.start(config['summoner_seed_id'])


