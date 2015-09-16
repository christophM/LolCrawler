import requests
import time

VERSION = "v2.2"



class RitoAPI:
    """Wraper for Riot APIs matchhistory and match endpoints"""

    def __init__(self, api_key, time_between_requests = 600/500, region="euw"):
        self.api_key = api_key
        self.region = region
        self.url_stem = 'https://{region}.api.pvp.net/api/lol/{region}/{version}/{endpoint}/{entity}'
        self.time_between_requests = time_between_requests
    
    def _build_request(self, endpoint, entity):
        return self.url_stem.format(region=self.region, version=VERSION, endpoint=endpoint, entity=entity)

    def _make_request(self, request_url, params={}):
        time.sleep(self.time_between_requests)
        params.update({'api_key': self.api_key})
        request = requests.get(request_url, params=params, verify=True)
        return request.json()
        
    def get_matchlist(self, summoner_id): 
        request_url = self._build_request(endpoint='matchlist/by-summoner', entity=summoner_id)
        return self._make_request(request_url)
    
    def get_match(self, match_id, include_timeline=True):
        request_url = self._build_request(endpoint='match', entity=match_id)
        return self._make_request(request_url, params={'includeTimeline': include_timeline})





