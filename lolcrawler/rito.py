import requests
import time

VERSION = "v2.2"


class ApiResponseError(Exception):
    """Most common errors with Rito API """
    errors = {400: "Bad request",
              401: "Unauthorized. Is something wrong with the API key?",
              404: "Data not found",
              429: "Too many requests. Maybe reduce number of requests per minute?",
              500: "Internal server error",
              503: "Service unavailable"}

    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        if self.status_code in self.errors.keys():
            return self.errors.get(self.status_code)
        else:
            return "Http request error with code %s" % (self.status_code)

class NotFoundError(ApiResponseError):
    pass

class RateLimitExceeded(ApiResponseError):
    pass

class RitoServerError(ApiResponseError):
    pass




class RitoAPI:
    """Wraper for Riot APIs matchhistory and match endpoints"""

    def __init__(self, api_key, time_between_requests = 600/500, region="euw"):
        self.api_key = api_key
        self.region = region
        self.url_stem = 'https://{region}.api.pvp.net/api/lol/{region}/{version}/{endpoint}/{entity}'
        self.time_between_requests = time_between_requests

    def _build_request(self, endpoint, entity, version=VERSION):
        return self.url_stem.format(region=self.region, version=version, endpoint=endpoint, entity=entity)

    def _make_request(self, request_url, params={}):
        time.sleep(self.time_between_requests)
        params.update({'api_key': self.api_key})
        request = requests.get(request_url, params=params)
        if request.status_code == 404:
            raise NotFoundError(request.status_code)
        elif request.status_code == 429:
            raise RateLimitExceeded(request.status_code)
        elif request.status_code in [500, 503]:
            raise RitoServerError(request.status_code)
        elif request.status_code != 200:
            raise ApiResponseError(request.status_code)
        return request.json()

    def get_matchlist(self, summoner_id, params={}):
        request_url = self._build_request(endpoint='matchlist/by-summoner', entity=summoner_id)
        return self._make_request(request_url, params=params)

    def get_match(self, match_id, include_timeline=False):
        request_url = self._build_request(endpoint='match', entity=match_id)
        return self._make_request(request_url, params={'includeTimeline': include_timeline})

    def get_league(self, league="challenger", queue="RANKED_SOLO_5x5"):
        request_url = self._build_request(endpoint='league', entity=league, version="v2.5")
        return self._make_request(request_url, params={'type': queue})
