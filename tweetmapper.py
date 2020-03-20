from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor

import twitter_credentials
import numpy as np
import pandas as pd
import json
import requests
import argparse

# # # # INPUT ARGUMENTS # # # #
parser = argparse.ArgumentParser()
parser.add_argument('NUMBER', help="Max number of tweets to query")
parser.add_argument('QUERY', help="String to query")
parser.add_argument('OUTPUT', help="Path to output csv")
args = parser.parse_args()

# # # # TWITTER CLIENT # # # #
class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

# # # # TWEET ANALYZER # # # #
class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """
    def tweets_to_data_frame(self, tweets):

        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['coordinates'] = np.array([tweet.coordinates for tweet in tweets])
        df['places'] = np.array([tweet.place for tweet in tweets])
        df['user location'] = np.array([tweet.user.location for tweet in tweets])

        return df

    def geo_data_to_df(self, places, lat, lon):
        coords_df = pd.DataFrame(list(zip(lat, lon)), columns =['Latitude', 'Longitude'])
        coords_df['Place Name'] = places
        return coords_df


if __name__ == '__main__':

# # # # AUTHENTICATION # # # #
    twitter_client = TwitterClient()
    tweet_analyzer=TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()


# # # # Set Parameters of Tweet Search # # # #
    max_tweets = int(args.NUMBER)
    query = args.QUERY
    tweets = [status for status in Cursor(api.search, q=query).items(max_tweets)]
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    print('Your query returned {} tweets'.format(len(tweets)))

# Make requests to Open Street Map's Nominatim Geocoder for Coordinates
    Places = []
    Lat = []
    Lon = []
    reqTemplate = "https://nominatim.openstreetmap.org/search?format=json&q={}&limit=1"

    for place in df['user location']:
        response = requests.get(reqTemplate.format(place.replace(" ", "+")))
        jsonResponse = response.json()
        if len(jsonResponse) != 0:
            print("{} location returns the following coordinates".format(place))
            print("\n")
            for item in response.json():
                print("Lat: {}".format(item["lat"]))
                print("Lon: {}".format(item["lon"]))
                print("\n")
                Lat.append(item["lat"])
                Lon.append(item["lon"])
                # Places.append(place)
                Places.append(item["display_name"])
        if len(jsonResponse) == 0:
            print("Nothing found for {}".format(place))
            print("\n")

# Add Latitude, Longitude, and Names of User Locations to Data Frame and CSV
    coords_df = tweet_analyzer.geo_data_to_df(Places, Lat, Lon)
    print(coords_df)
    coords_df.to_csv(r'args.OUTPUT')
