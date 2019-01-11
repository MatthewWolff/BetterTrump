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
        self.api, self.me = self._verify()
        self.log_file = f"{self.me}.log"

    def _verify(self):
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

        api = self._authorize()
        try:
            me = api.me().screen_name
        except TweepError as e:
            raise ValueError("API might be disabled or you have invalid keys:"
                             f"\n\t{self._extract_tweepy_error(e)}")

        thread.join()  # lol
        print(colors.white(" verified\n") +
              colors.cyan("starting up bot ") + colors.white(f"@{me}!\n"))
        return api, me  # api, the bot's handle

    def _authorize(self):
        """
        Uses keys to create an API accessor and returns it
        :return: an API object used to access the Twitter API
        """
        auth = tweepy.OAuthHandler(self.keys["consumer_key"], self.keys["consumer_secret"])
        auth.set_access_token(self.keys["access_token"], self.keys["access_token_secret"])
        return tweepy.API(auth)

    def _is_replied(self, tweet):
        """
        Check if a tweet has been replied to (favorite'd)
        :param tweet: the status object to check the reply status of
        :return: a boolean value indicating if the status has been replied to
        """
        favorites = [x.id for x in self.api.favorites()]
        return tweet.id in favorites

    def _mark_replied(self, tweet_id):
        """
        Favorites a tweet to mark it "replied" to. This prevents the bot from replying more than once
        :param tweet_id: the tweet that has been addressed
        """
        self.api.create_favorite(tweet_id)

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
                print(colors.red(f"failed to delete: {status.id}"))

    def clear_favorites(self):
        """
        DANGER: removes all favorites from current bot account
        """
        response = None
        while response != "y":
            response = input(colors.red("ARE YOU SURE YOU WANT TO ERASE ALL FAVORITES? (y/n)"))
        [self.api.destroy_favorite(x.id) for x in self.api.favorites()]
        print(colors.white("erased all favorites"))

    def is_active(self):
        """
        The bot tries not to tweet at times when no one will see
        :return: whether the bot is in its active period
        """
        current_time = datetime.now().hour
        early = self.active[0]
        late = self.active[-1]
        return early <= current_time < late

    @staticmethod
    def _divide_tweet(long_tweet, at=None):
        """
        A method for exceptionally long tweets
        :rtype: the number of tweets, followed by the tweets
        :param at: the person you're responding to/at
        :param long_tweet: the long-ass tweet you're trying to make
        :return: the number of tweets and an array of tweets
        """

        # too big!
        if len(long_tweet) > 1400:
            return 0, None

        handle = f"@{at} " if at else ""

        def make_new_tweet(sentence_list):
            tweet = list()
            while len(sentence_list) > 0 and len("\n".join(tweet)) + len(sentence_list[0] + " ") <= TWEET_MAX_LENGTH:
                tweet.append(sentence_list.pop(0))
            return "\n".join(tweet)

        tweets = list()
        verdicts = long_tweet.split("\n")
        verdicts[0] = handle + verdicts[0]
        while len(verdicts) > 0:
            tweets.append(make_new_tweet(verdicts))
        return len(tweets), tweets

    def tweet(self, tweet, at=None):
        """
        General tweeting method. It will divide up long bits of text into multiple messages,
        and return the first tweet that it makes. Multi-tweets (including to other people)
        will have second and third messages made in response to self.
        :param at: who the user is tweeting at
        :param tweet: the text to tweet
        :return: the first tweet, if successful; else, none
        """
        if tweet.strip() == "":
            return

        num_tweets, tweets = self._divide_tweet(tweet, at)
        if num_tweets > 0:
            # replace @'s with #'s and convert unicode emojis before tweeting
            [self.api.update_status(tw.replace("@", "#").encode("utf-8")) for tw in tweets]
            self.log(f"Tweeted: {' '.join(tweets)}")
            return tweets[0]

    @staticmethod
    def _extract_tweepy_error(e):
        return e.response.reason

    def log(self, activity):
        with open(self.log_file, "a") as l:
            l.write(f"{strftime('[%Y-%m-%d] @ %H:%M:%S')} {activity}\n")

    def log_error(self, error_msg):
        self.log(colors.red(f"ERROR => {error_msg}"))
