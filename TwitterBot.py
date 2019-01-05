import sys
from datetime import datetime
from threading import Thread
from time import sleep, strftime

import auxiliary.colors as colors
import tweepy
from tweepy import TweepError

# constants
TWEET_MAX_LENGTH = 280


class TwitterBot:
    def __init__(self, api_keys, active_hours=range(24)):
        self.keys = api_keys
        self.active = active_hours
        self.api, self.me = self.verify()
        self.log = f"{self.me}_log.txt"

    def authorize(self):
        """
        Uses keys to create an API accessor and returns it
        :return: an API object used to access the Twitter API
        """
        auth = tweepy.OAuthHandler(self.keys["consumer_key"], self.keys["consumer_secret"])
        auth.set_access_token(self.keys["access_token"], self.keys["access_token_secret"])
        return tweepy.API(auth)

    def verify(self):
        """
        Verifies that the user has valid credentials for accessing Tweepy API
        :return: a tuple containing an API object and the handle of the bot
        """

        def loading():
            for _ in range(3):
                print(colors.yellow("."), end="")
                sys.stdout.flush()
                sleep(0.5)

        sys.stdout.write(colors.yellow("verifying credentials"))
        thread = Thread(target=loading())  # lol
        thread.daemon = True  # kill this thread if program exits
        thread.start()

        api = self.authorize()
        try:
            me = api.me().screen_name
        except TweepError as e:
            err = e[0][0]["message"]
            raise ValueError(f"API might be disabled or you have invalid keys:\n\t{err}")

        thread.join()  # lol
        print(colors.white(" verified\n") + colors.cyan("starting up bot ") + colors.white("@" + me + "!\n"))
        return api, me  # api, the bot's handle, the mimicked's name, full version of user's name

    def tweet(self, tweet, at=None):
        """
        General tweeting method. It will divide up long bits of text into multiple messages, and return the first tweet
        that it makes. Multi-tweets (including to other people) will have second and third messages made in response
        to self.
        :param at: who the user is tweeting at
        :param tweet: the text to tweet
        :return: the first tweet if successful
        """
        if tweet.strip() == "":
            return

        num_tweets, tweets = self.divide_tweet(tweet, at)
        if num_tweets > 0:
            # replace @'s with #'s and convert unicode emojis before tweeting
            [self.api.update_status(tw.replace("@", "#").encode("utf-8")) for tw in tweets]
            self.log_activity(f"{strftime('[%Y-%m-%d] @ %H:%M:%S')} Tweeted: " + " ".join(tweets))
            return tweets[0]  # return first tweet - multi-tweets will be responding to it

    def log_activity(self, activity):
        with open(self.log, "w") as log:
            log.write(activity)

    def clear_tweets(self):
        """
        DANGER: removes all tweets from current bot account
        """
        response = None
        while response != "y":
            response = input(colors.red("ARE YOU SURE YOU WANT TO ERASE ALL TWEETS? (y/n)"))

        for status in tweepy.Cursor(self.api.user_timeline).items():
            try:
                self.api.destroy_status(status.id)
                print(colors.white("deleted successfully"))
            except TweepError:
                print(colors.red(f"Failed to delete: {status.id}"))

    def is_active(self):
        """
        The bot tries not to tweet at times when no one will see
        :return: whether the bot is in its active period
        """
        current_time = datetime.now().hour
        early = self.active[0]
        late = self.active[-1]
        return early <= current_time < late

    def divide_tweet(self, long_tweet, at=None):
        """
        A method for exceptionally long tweets
        :rtype: the number of tweets, followed by the tweets
        :param at: the person you're responding to/at
        :param long_tweet: the long-ass tweet you're trying to make
        :return: an array of up to 3 tweets
        """
        # 1 tweet
        handle = "@" + at + " " if at else ""
        my_handle = "@" + self.me
        numbered = len("(x/y) ")

        single_tweet_length = (TWEET_MAX_LENGTH - len(handle))
        first_tweet_length = (TWEET_MAX_LENGTH - len(handle) - numbered)
        self_tweet_length = (TWEET_MAX_LENGTH - len(my_handle) - numbered)
        two_tweets_length = first_tweet_length + self_tweet_length
        three_tweets_length = two_tweets_length + self_tweet_length

        # 1 tweet
        if len(long_tweet) <= single_tweet_length:
            return 1, [handle + long_tweet]
        # too many characters (edge case)
        elif len(long_tweet) >= three_tweets_length:
            return 0, None
        # 3 tweets
        elif len(long_tweet) > two_tweets_length:
            return 3, [handle + "(1/3) "
                       + long_tweet[:first_tweet_length],
                       my_handle + "(2/3) "
                       + long_tweet[first_tweet_length: two_tweets_length],
                       my_handle + "(3/3) "
                       + long_tweet[two_tweets_length: len(long_tweet)]]
        # 2 tweets
        else:
            return 2, [handle + "(1/2) "
                       + long_tweet[: first_tweet_length],
                       my_handle + "(2/2) "
                       + long_tweet[first_tweet_length: len(long_tweet)]]
