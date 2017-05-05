#!/usr/bin/env python
# -*- encoding: utf8 -*-


from twython import Twython, TwythonRateLimitError
import sexmachine.detector as gender
from analyze import declared_gender, split, rm_punctuation
import argparse
from unidecode import unidecode
import json


APP_KEY = "YOUR_APP_KEY"
APP_SECRET = "YOUR_APP_PASS"
twitter = Twython(APP_KEY, APP_SECRET, oauth_version=1)
detector = gender.Detector(case_sensitive=False)

result = {'nonbinary': 0,
          'men': 0,
          'women': 0,
          'andy': 0}

def defineOptions():
    parser = argparse.ArgumentParser( description='Gender Analyze Twitter Tool' )
    parser.add_argument('screen_name', type=str, help="Twitter account name to be analyzed")
    args = parser.parse_args()
    return (args, parser)


def getFollowers( name ):
    return twitter.get_followers_list(screen_name=name, count=200,cursor=-1)


def getFriends( name ):
    return twitter.get_friends_list(screen_name=name, count=200, cursor=-1)



def usersInfo( userList ):
    userDict = {}
    for user in userList:
        userDict[ user["screen_name"] ] = {}
        userDict[ user["screen_name"] ]["name"]             = user["name"]
        userDict[ user["screen_name"] ]["lang"]             = user["lang"]
        userDict[ user["screen_name"] ]["location"]         = user["location"]
        userDict[ user["screen_name"] ]["friends_count"]    = user["friends_count"]
        userDict[ user["screen_name"] ]["followers_count"]  = user["followers_count"]
        userDict[ user["screen_name"] ]["favourites_count"] = user["favourites_count"]
        userDict[ user["screen_name"] ]["statuses_count"]   = user["statuses_count"]
        #Guess the Gender
        g = declared_gender( user["description"] )
        if g == 'andy':
            for name, country in [
                (split(user["name"]), None),
                (user["name"], None),
                (unidecode(user["name"]), None),
                (split(unidecode(user["name"])), None),
            ]:
                g = detector.get_gender(name, country)
                if g != 'andy':
                    # Not androgynous.
                    break
                g = detector.get_gender(rm_punctuation(name), country)
                if g != 'andy':
                    # Not androgynous.
                    break
        userDict[ user["screen_name"] ]["gender"]   = g

        # uDict[args.screen_name]['total_count']   = ''
        # uDict[args.screen_name]['male_count']   = ''
        # uDict[args.screen_name]['female_count']   = ''
        # uDict[args.screen_name]['nonbinary_count']   = ''

    return userDict


if __name__ == "__main__":
    global args
    (args, parser) = defineOptions()


    followers = getFollowers( args.screen_name )
    followersInfo = usersInfo( followers["users"] )
    followersInfo['male_count']   = ''
    followersInfo['female_count'] = ''

    friends   = getFriends( args.screen_name )
    friendsInfo = usersInfo( friends["users"] )
    friendsInfo['male_count']   = ''
    friendsInfo['female_count'] = ''

    uDict = {}
    uDict[args.screen_name] = {}
    uDict[args.screen_name]['name']             = ''
    uDict[args.screen_name]['lang']             = ''
    uDict[args.screen_name]['location']         = ''
    uDict[args.screen_name]['friends_count']    = ''
    uDict[args.screen_name]['followers_count']  = ''
    uDict[args.screen_name]['favourites_count'] = ''
    uDict[args.screen_name]['statuses_count']   = ''
    uDict[args.screen_name]['gender']   = ''

    # Total count intersection of friends and followers
    uDict[args.screen_name]['total_count']   = ''
    uDict[args.screen_name]['male_count']   = ''
    uDict[args.screen_name]['female_count']   = ''
    uDict[args.screen_name]['nonbinary_count']   = ''

    uDict[args.screen_name]['followers_list']   = followersInfo
    uDict[args.screen_name]['friends_list']     = friendsInfo

    f = open( args.screen_name+'.json' , 'w')
    f.write( json.dumps(uDict) )
    f.close()
