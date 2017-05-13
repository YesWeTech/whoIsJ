#!/usr/bin/env python
# -*- encoding: utf8 -*-


from twython import Twython, TwythonRateLimitError
import sexmachine.detector as gender
import tweepy
from tweepy import OAuthHandler
from analyze import declared_gender, split, rm_punctuation
import argparse
from unidecode import unidecode
import json
from index import guessGender


consumer_key = 'YOUR_APP_KEY'
consumer_secret = 'YOUR_APP_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_TOKEN_SECRET'

twitter = Twython(consumer_key, consumer_secret, oauth_version=1)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

detector = gender.Detector(case_sensitive=False)


def defineOptions():
    parser = argparse.ArgumentParser( description='Gender Analyze Twitter Tool' )
    parser.add_argument('screen_name', type=str, help="Twitter account name to be analyzed")
    parser.add_argument('count', type=int, help="Last N-tweets", default=20)
    args = parser.parse_args()
    return (args, parser)


if __name__ == "__main__":
    global args
    (args, parser) = defineOptions()

    female_c = 0
    male_c = 0
    nonbinary_c = 0
    undefined_c = 0


    # Get users that interacted with N last tweets
    users = {}
    timeline = api.user_timeline(screen_name=args.screen_name, count=args.count, include_rts=True)
    for tweet in timeline:
        # hashtags = tweet._json['hashtags']
         for a in tweet._json['entities']['user_mentions']:
             if not users.has_key(a['screen_name']):
                 users[a['screen_name']] = {}


    for u in users.keys():
        userInfo = api.get_user(u)
        users[u]['location']    = userInfo.location
        users[u]['name']        = userInfo.name
        users[u]['description'] = userInfo.description
        g = guessGender( userInfo.name, userInfo.description, userInfo.location )
        users[u]['gender']      = g
        # Conteo
        if g == "female": female_c += 1
        elif g == "male": male_c += 1
        elif g == "nonbinary": nonbinary_c += 1
        elif g == "undetermined": undefined_c += 1

    total_count = len(users)
    users['total_count']        =  total_count
    users['female_count']       =  female_c
    users['male_count']         =  male_c
    users['nonbinary_count']    =  nonbinary_c
    users['undefined_count']    =  undefined_c

    if len(users) > 0:
        female_rate   = str((female_c  * 100) / total_count)+"%"
        male_rate     = str((male_c * 100) / total_count)+"%"
        nonbinary_rate= str((nonbinary_c * 100) / total_count)+"%"
        undefined_rate= str((undefined_c * 100) / total_count)+"%"

        users['female_rate']       =  female_rate
        users['male_rate']         =  male_rate
        users['nonbinary_rate']    =  nonbinary_rate
        users['undefined_rate']    =  undefined_rate


    f = open( '../out/'+args.screen_name+'_tweets.json' , 'w')
    f.write( json.dumps(users) )
    f.close()
