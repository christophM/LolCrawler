from lolcrawler import LolCrawler
from rito_api import RitoAPI
from config import config


if __name__=="__main__":
    api = RitoAPI(config['api_key'])
    crawler =  LolCrawler(api)
    crawler.start(config['SUMMONER_SEED_ID'])


