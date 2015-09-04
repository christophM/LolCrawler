import requests
import time
import json

VERSION = "v2.2"
SECONDS = 600.0
N_REQUESTS = 500
COOLDOWN_TIME = SECONDS / N_REQUESTS


class RitoAPI:
    """Wraper for Riot APIs matchhistory and match endpoints"""

    def __init__(self, api_key, region="euw"):
        self.api_key = api_key
        self.region = region
        self.url_stem = 'https://{region}.api.pvp.net/api/lol/{region}/{version}/{endpoint}/{entity}'
    
    def _build_request(self, endpoint, entity):
        return self.url_stem.format(region=self.region, version=VERSION, endpoint=endpoint, entity=entity)

    def _make_request(self, request_url, params={}):
        time.sleep(COOLDOWN_TIME)
        params.update({'api_key': self.api_key})
        request_text = requests.get(request_url, params=params, verify=True).text
        return json.loads(request_text)

    def get_matchhistory(self, summoner_id, begin_index=None, end_index=None):
        request_url = self._build_request(endpoint='matchhistory', entity=summoner_id)
        return self._make_request(request_url, params={'beginIndex': begin_index, 'endIndex': end_index})

    def get_complete_matchhistory(self, summoner_id):
        """Loop through paginated matchhistory"""
        begin_index = 0
        end_index = 15
        match_history = self.get_matchhistory(summoner_id, begin_index=begin_index, end_index=end_index)
        new_matches = match_history["matches"]
        matches = new_matches

        while(len(new_matches) == 15):
            begin_index += 15
            end_index += 15
            match_history = self.get_matchhistory(summoner_id, begin_index=begin_index, end_index=end_index)
            new_matches = match_history["matches"]
            matches += new_matches
        return matches
    
    def get_match(self, match_id, include_timeline=True):
        request_url = self._build_request(endpoint='match', entity=match_id)
        return self._make_request(request_url, params={'includeTimeline': include_timeline})





