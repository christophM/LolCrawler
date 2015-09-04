# LolCrawler

Crawls League of Legends match histories and match data


## What it does
1. Start with seed summoner
2. Download complete match history of chosen summoner in ./matchhistories
3. Save match history of summoner
4. Choose random match 
5. Download and save match in ./matches
6. Choose random player from downloaded match and continue with step 2

## Usage
Place your Riot API key in config.js. LolCrawler needs a region and a summoner id to get started. The config file provides a summoner seed for Europe West (EUW). Start the script in the terminal by typing:

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


LolCrawler isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.




