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
    args = parser.parse_args()
    return (args, parser)

def guessGender( name, description=None, country=None ):
    g = "undetermined"
    g = declared_gender( description )
    if g == 'andy':
        for name, country in [
            (split(name), None),
            (name, None),
            (unidecode(name), None),
            (split(unidecode(name)), None),
        ]:
            g = detector.get_gender(name, country)
            if g != 'andy':
                # Not androgynous.
                break
            g = detector.get_gender(rm_punctuation(name), country)
            if g != 'andy':
                # Not androgynous.
                break
    if g != 'andy':
        return g
    else:
        return "undetermined"


def getUserInfo( name ):
    return api.get_user( name )


def getFollowers( name ):
    return twitter.get_followers_list(screen_name=name, count=200,cursor=-1)


def getFriends( name ):
    return twitter.get_friends_list(screen_name=name, count=200, cursor=-1)


def usersInfo( userList ):
    female_count = 0
    male_count = 0
    nonbinary_count = 0
    undefined_count = 0
    total_count = 0

    userDict = {}
    for user in userList:
        userDict[ user["screen_name"] ] = {}
        userDict[ user["screen_name"] ]["name"]             = user["name"]
        userDict[ user["screen_name"] ]["id"]               = user["id"]
        userDict[ user["screen_name"] ]["lang"]             = user["lang"]
        userDict[ user["screen_name"] ]["location"]         = user["location"]
        userDict[ user["screen_name"] ]["friends_count"]    = user["friends_count"]
        userDict[ user["screen_name"] ]["followers_count"]  = user["followers_count"]
        userDict[ user["screen_name"] ]["favourites_count"] = user["favourites_count"]
        userDict[ user["screen_name"] ]["statuses_count"]   = user["statuses_count"]
        g = guessGender(  user["name"], user["description"], user["location"] )
        userDict[ user["screen_name"] ]["gender"]           = g

        if g == "female":       female_count += 1
        elif g == "male":       male_count += 1
        elif g == "nonbinary":  nonbinary_count += 1
        elif g == "undetermined":  undefined_count += 1

        total_count += 1

    userDict[ "female_count" ]      =  female_count
    userDict[ "male_count" ]        =  male_count
    userDict[ "nonbinary_count" ]   =  nonbinary_count
    userDict[ "undefined_count" ]   =  undefined_count
    userDict[ "total_count" ]       =  total_count

    if total_count > 0:
        userDict[ "female_rate" ]   = str((female_count * 100) / total_count)+"%"
        userDict[ "male_rate" ]     = str((male_count * 100) / total_count)+"%"
        userDict[ "nonbinary_rate" ]= str((nonbinary_count * 100) / total_count)+"%"
        userDict[ "undefined_rate" ]= str((undefined_count * 100) / total_count)+"%"

    return userDict

def getDiversityOfIntersect( dict1, dict2 ):
    interDict = {}
    # Calc intersect
    for name_key in dict1.keys():
        if not name_key == "female_count" and \
            not name_key == "male_count" and \
            not name_key == "nonbinary_count" and \
            not name_key == "undefined_count" and \
            not name_key == "total_count" and \
            not name_key == "female_rate" and \
            not name_key == "male_rate" and \
            not name_key == "nonbinary_rate" and \
            not name_key == "undefined_rate" and \
            not interDict.has_key(name_key):
            interDict[name_key] = dict1[name_key]["gender"]
    for name_key in dict2.keys():
        if not name_key == "female_count" and \
            not name_key == "male_count" and \
            not name_key == "nonbinary_count" and \
            not name_key == "undefined_count" and \
            not name_key == "total_count" and \
            not name_key == "female_rate" and \
            not name_key == "male_rate" and \
            not name_key == "nonbinary_rate" and \
            not name_key == "undefined_rate" and \
            not interDict.has_key(name_key):
            interDict[name_key] = dict2[name_key]["gender"]

    # Get diversity info
    female_count = 0
    male_count = 0
    nonbinary_count = 0
    undefined_count = 0
    total_count = 0

    for key in interDict.keys():
        if interDict[key] == "female":
            female_count += 1
        elif interDict[key] == "male":
            male_count += 1
        elif interDict[key] == "nonbinary":
            nonbinary_count += 1
        elif interDict[key] == "undetermined":
            undefined_count += 1

        total_count += 1

    if total_count > 0:
        female_rate   = str((female_count * 100) / total_count)+"%"
        male_rate     = str((male_count * 100) / total_count)+"%"
        nonbinary_rate= str((nonbinary_count * 100) / total_count)+"%"
        undefined_rate= str((undefined_count * 100) / total_count)+"%"

    return (female_count,male_count,nonbinary_count,undefined_count,female_rate,male_rate,nonbinary_rate,undefined_rate,total_count)



if __name__ == "__main__":
    global args
    (args, parser) = defineOptions()

    followers = getFollowers( args.screen_name )
    followersInfo = usersInfo( followers["users"] )

    friends   = getFriends( args.screen_name )
    friendsInfo = usersInfo( friends["users"] )

    userInfo = getUserInfo( args.screen_name )
    uDict = {}
    uDict[args.screen_name] = {}

    uDict[args.screen_name]['name']             = userInfo.name
    uDict[args.screen_name]['id']               = userInfo.id
    uDict[args.screen_name]['lang']             = userInfo.lang
    uDict[args.screen_name]['location']         = userInfo.location
    uDict[args.screen_name]['friends_count']    = userInfo.friends_count
    uDict[args.screen_name]['followers_count']  = userInfo.followers_count
    uDict[args.screen_name]['favourites_count'] = userInfo.favourites_count
    uDict[args.screen_name]['statuses_count']   = userInfo.statuses_count
    uDict[args.screen_name]['gender']           = guessGender( userInfo.name, userInfo.description, userInfo.location )

    ( female_c, male_c, nonbinary_c, undefined_c, female_r, male_r, nonbinary_r, undefined_r, total_c ) = getDiversityOfIntersect( followersInfo, friendsInfo )


    uDict[args.screen_name]['total_count']     = total_c

    uDict[args.screen_name]['female_count']    = female_c
    uDict[args.screen_name]['male_count']      = male_c
    uDict[args.screen_name]['nonbinary_count'] = nonbinary_c
    uDict[args.screen_name]['undefined_count'] = undefined_c

    uDict[args.screen_name]['female_rate']     = female_r
    uDict[args.screen_name]['male_rate']       = male_r
    uDict[args.screen_name]['nonbinary_rate']  = nonbinary_r
    uDict[args.screen_name]['undefined_rate']  = undefined_r


    uDict[args.screen_name]['followers_list']   = followersInfo
    uDict[args.screen_name]['friends_list']     = friendsInfo

    f = open( '../out/'+args.screen_name+'.json' , 'w')
    f.write( json.dumps(uDict) )
    f.close()
