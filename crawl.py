from lolcrawler import LolCrawler
from rito_api import RitoAPI
from config import config


if __name__=="__main__":
    time_between_requests = config['rate_limit']['seconds'] / float(config['rate_limit']['n_requests'])
    api = RitoAPI(config['api_key'], time_between_requests)
    crawler =  LolCrawler(api, get_complete_matchhistory=config['get_complete_matchhistory'])
    crawler.start(config['SUMMONER_SEED_ID'])


