#!/usr/bin/env python3
from random import uniform as randunif
from time import sleep

import markovify
from TwitterBot import TwitterBot
from keys import key
from auxiliary.prepare_corpus import process_tweets


def make_model(corpus):
    text_model = markovify.Text(corpus, state_size=4)
    print("Generated markov model...")
    return text_model


if __name__ == "__main__":
    markov_model = make_model(corpus=str(process_tweets()))  # http://www.trumptwitterarchive.com
    bot = TwitterBot(key, active_hours=range(7, 21))

    while True:
        if bot.is_active():
            new_tweet = markov_model.make_short_sentence(min_chars=20, max_chars=200, tries=100)
            print(bot.tweet(new_tweet))

        # wait for 1 hr + randunif(1,-1) * 30 min
        tweet_delay = 60 * 60 + randunif(-1, 1) * 60 * 30
        sleep(tweet_delay)
