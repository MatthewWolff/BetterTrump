#!/usr/bin/python
import json
import re

handle = "realDonaldTrump"
folder = "auxiliary" # folder that the user.json is in relative to run_bot.py

def clean(tweet):
    tw = re.sub("Donald J\. Trump|\(cont\)", "", tweet["text"])  # ignore when he quotes himself
    tw = re.sub("(https?://.*)|(www\..*)|(t\.co.*)|(amzn\.to.*)( |$)", "", tw)  # remove links
    tw = re.sub("RE:|(rt|Rt|RT) @.+ | ?RT|Rt ?|^@.+ ", "", tw)  # ignore @'s if it's a direct reply
    tw = re.sub("\.@", "@", tw)
    tw = re.sub("\n", " ", tw)
    tw = re.sub(" ?#", " #", tw)
    tw = re.sub("\.\.\.+", "...", tw)  # collapses long ellipses
    tw = re.sub(" ?&amp; ?", " & ", tw)  # convert into &
    # tw = re.sub("!+", " ! ", tw)  # exclamation!! (collapses extra)
    # tw = re.sub("\?+", " ? ", tw)  # question marks?? (collapses extra)
    tw = re.sub("&lt;", "<", tw)
    tw = re.sub("&gt;", ">", tw)
    tw = re.sub("$", " ", tw)
    last = tw[-5:].strip()  # check to see if we need to add a period to their tweet
    if "..." not in last and "?" not in last and "!" not in last and "." not in last:
        tw += ". "
    tw = re.sub(" +\. +", "", tw)
    return tw


def useful(tw):
    return "Donald Trump" not in tw["text"]  # ignore third person speech & retweets


def process_tweets():
    with open(f"{folder}/{handle}.json") as raw_corpus:
        tweets = json.load(raw_corpus)
    processed_corpus = [clean(tweet) for tweet in tweets if useful(tweet)]
    full_corpus = " ".join(processed_corpus)  # assemble into singe blob of text
    return re.sub(" +", " ", full_corpus).encode("utf-8")  # collapse extra spaces and encode as unicode


if __name__ == "__main__":
    with open(f"{handle}_corpus.txt", "wb") as out:
        out.write(process_tweets())
