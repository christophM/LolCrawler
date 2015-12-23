# LolCrawler
Crawls League of Legends summoner match lists and match data and stores the data


## What it does
1. Start with the seed summoner as defined in config.py
2. Download match list of the chosen summoner and store it in MongoDB
3. Choose random match from the match list
4. Download match via API and store it in MongoDB
5. Choose random player from the downloaded match and continue with step 2

## Usage
Place your Riot API key in config.py. LolCrawler needs a region and a summoner id to start crawling. The config.py file provides a summoner seed for Europe West (EUW). You need to have MongoDB installed for storing the match and match list JSON.

Start crawling:

```bash
python crawl.py
```

Run the script in the background by using nohup:
```bash
nohup python -u crawl.py &
```

Check if the script is still running with:
```bash
ps ax | grep crawl.py
```

And kill LolCrawler by checking if the script is still running, checking the process id and then type:
```bash
kill <process-id>
```

If something goes wrong, have a look at the log file named crawler.log.


## Changelog
### v0.6
- Adding patch fields to match, extracted from the field "matchVersion"
  - "patch": The patch version as a string, for example "5.24"
  - "patchMajorNumeric": The major patch version as integer, resembling the season, for example 5
  - "patchMinorNumeric": The minor patch version as integer, for example 24
### v0.5
- Be smarter about match and summoner sampling
- By default, don't fetch the timeline
- Sample only from the latest matches of a summoner
- Introduce logging

### v0.4
- If there are already matchlists inserted in MongoDB, start with latest summoner id as seed summoner, instead of seed summoner id from config file
- Move files in own module

### v0.3
- Change from Riot Api's matchhistory endpoint to matchlist, since matchhistory endpoint will be deprecated starting 2015/09/22
- Be more intelligent about error handling and make crawler more robust

### v0.2
- Write to MongoDB, not to disk
### v0.1
- Initial release

## Disclaimer
LolCrawler isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.




