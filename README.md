# BetterTrump Bot
Trump tweets a lot. It's repetitive and often non-sensical—perfect for a Markov model!  
**NOTE: this bot uses a Markov chain package. If you'd like to see my hand-implemented version, see** [MarkovTweets](https://github.com/MatthewWolff/MarkovTweets).  

## Requirements:
* Python 3
* Tweepy API credentials
* Markovify package

### Where'd the tweets come from?
While Trump tweets a lot, he often deletes things, too. Someone came up with the idea of [archiving all of his tweets and making them easily downloadable](http://www.trumptwitterarchive.com). Using a JSON file downloaded from there on January 3rd, 2019, I wrote `prepare_corpus.py` to comb through and remove fodder (links to websites and manual retweets) and combine all the tweets into a corpus. A small `TwitterBot` class I wrote was then used host a markov model created by [jsvine's markovify package](https://github.com/jsvine/markovify).   

### Twitter API credentials
In order to use the bot, you must have your own credentials from 
[Twitter's developer site](https://dev.twitter.com) and place them in a file called 
`keys.py` as a dictionary object called key. Additionally, you'll need the `tweepy` module. 
See below for that.

```python
key = {
    "consumer_secret": "abcdefghijklmnopqrstuvwxyz",
    "access_token_secret": "1234567890",
    "consumer_key": "Nequeporroquisquamestquidolorem",
    "access_token": "ipsumquiadolorsitamet"
}
```

### Installing `markovify` and `tweepy`
```bash
$ pip install markovify tweepy
```

### To run, clone the repo and execute the following:
```bash
$ python run_bot.py
```

## tweet\_as
Although twitter limits the number of tweets you can scrape to 3200, you can emulate someone's tweets off of that!  
Use `tweet_as` to select any (public) twitter user and create some tweets from them!

```
$ tweet_as realdonaldtrump
generating markov model for realdonaldtrump with up to 3200 tweets!
corpus size: 42615 characters

...I campaigned on Border Security for other countries - taking advantage of U.S. troops from the Never Ending Wars.
After many years ago.
Many stories, like with the Shutdown and finish funding.
This is exactly what he promised, and I in Iraq and Germany.
Here we go with Mitt Romney, but so is the wheel.
Do you think it's just luck that gas prices are low and expected to go down this year.
I also look forward to my next summit with Chairman Kim!
Dr. Sebastian Gorka, a very long time.
If we had a Wall, calling it old fashioned.
No thanks to the truth of the Witch Hunt is the Fed.
Have the Democrats that there was a great Christmas!
A REAL scandal is the greatest Country in the Oval Office right now.
These great Americans left their jobs to serve in the first place!
The reporting has been reported by the media.
We brought or gave NO hats as the Fake News tries so hard & getting so little credit!
I am in the Oval Office right now.
Go back to Washington from all parts of the resources that he is a total Obstruction of Justice.
2018 is being fixed!
```
