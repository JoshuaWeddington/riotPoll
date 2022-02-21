import constants
import requests
import pandas as pd
import numpy as np
import time
import datetime
import sys


if constants.key == "-- Insert Key Here --":
    sys.exit("Key not changed, insert proper key")
else:
    key = constants.key

combinedIDs = pd.DataFrame(columns = ["summonerId"])
#Get challengers and parse for their summonerIDs
def getChallengers(combinedIDs):
    challengers = requests.get(
        "https://na1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=" + key)
    challengers = challengers.json()
    challengers = pd.DataFrame.from_dict(challengers["entries"])
    challengerIDs = pd.DataFrame(challengers["summonerId"])
    combinedIDs = combinedIDs.append(challengerIDs)
    time.sleep(1.5)
    print("Challengers done")
    return combinedIDs

def getGM(combinedIDs):
    grandmasters = requests.get("https://na1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key=" + key)
    grandmasters = grandmasters.json()
    grandmasters = pd.DataFrame.from_dict(grandmasters["entries"])
    grandmasterIDs = pd.DataFrame(grandmasters["summonerId"])
    combinedIDs = combinedIDs.append(grandmasterIDs, ignore_index = True)
    time.sleep(1.5)
    print("Grandmasters done")
    return combinedIDs

def getMasters(combinedIDs):
    masters = requests.get("https://na1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key=" + key)
    masters = masters.json()
    masters = pd.DataFrame.from_dict(masters["entries"])
    masterIDs = pd.DataFrame(masters["summonerId"])
    combinedIDs = combinedIDs.append(masterIDs, ignore_index = True)
    time.sleep(1.5)
    print("Masters done")
    return combinedIDs

def getPlatAndDiamond(combinedIDs):
    ranks = ['DIAMOND', 'PLATINUM']
    divisions = ['I', 'II', 'III', 'IV']
    for i in range(len(ranks)):
        for j in range(len(divisions)):
            for k in range(1, 4):
                currentPage = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/" + ranks[i] + "/" + divisions[j] +"?page=" + str(k) + "&api_key=" + key)
                currentPage = currentPage.json()
                currentPage = pd.DataFrame.from_dict(currentPage)
                currentPageIDs = pd.DataFrame(currentPage["summonerId"])
                combinedIDs = combinedIDs.append(currentPageIDs, ignore_index = True)
                time.sleep(1.5)
                print(ranks[i] + " " + divisions[j] + " page " + str(k) + " done")
    return combinedIDs

if constants.queryChallengers:
    combinedIDs = getChallengers(combinedIDs)
if constants.queryGrandmasters:
    combinedIDs = getGM(combinedIDs)
if constants.queryMasters:
    combinedIDs = getMasters(combinedIDs)
if constants.queryPlatDiamond:
    combinedIDs = getPlatAndDiamond(combinedIDs)

#Use summonerIDs to get puuids
puuids = pd.DataFrame(columns = ['puuid'])
for i in range(10):
    requestURL = ("https://na1.api.riotgames.com/lol/summoner/v4/summoners/" + combinedIDs.iloc[i] + "?api_key=" + key)
    rawRequest = requests.get(requestURL['summonerId'])
    rawRequest = rawRequest.json()
    puuid = rawRequest["puuid"]
    puuids.loc[i] = puuid
    print("puuid iteration: " + str(i))
    time.sleep(1.5)
   
#Use PUUIDs to get match IDs
matchIDs = pd.DataFrame(columns = ['matchID'])
for i in range(len(puuids)):
    requestURL = ("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuids.iloc[i] + "/ids?queue=420&start=0&count=20&api_key=" + key)
    matchRequest = requests.get(requestURL['puuid'])
    matchRequest = matchRequest.json()
    matches = pd.DataFrame.from_dict(matchRequest)
    matches = matches.set_axis(['matchID'], axis = 1, inplace = False)
    matchIDs = matchIDs.append(matches, ignore_index = True)
    print("match iteration: " + str(i))
    time.sleep(1.5)
   
#Remove duplicates
matchIDs = matchIDs.drop_duplicates()
matchIDs = matchIDs.reset_index(drop = True)

def parseDragons(events, parsedTimeline):
    team1Count = 0
    team2Count = 0
    parsedTimeline['team1Dragons'] = np.nan
    parsedTimeline['team2Dragons'] = np.nan
    timestamps = pd.DataFrame()
    for i in range(len(events)):
        tempEvent = events[i]
        for j in range(len(tempEvent)):
            indEvent = tempEvent[j]
            #attempts to generalize the rectification of double counting events
            if len(timestamps) == 0:
                if (indEvent["type"] == "ELITE_MONSTER_KILL" and indEvent["monsterType"] == "DRAGON" and indEvent["killerTeamId"] == 100):
                    tempTime = pd.Series(indEvent['timestamp'])
                    timestamps = timestamps.append(tempTime, ignore_index = True)
                    team1Count = team1Count + 1
                    timeIndex = (indEvent['timestamp'] // 60000) + 1
                    parsedTimeline.loc[timeIndex, 'team1Dragons'] = team1Count
                if (indEvent["type"] == "ELITE_MONSTER_KILL" and indEvent["monsterType"] == "DRAGON" and indEvent["killerTeamId"] == 200):
                    tempTime = pd.Series(indEvent['timestamp'])
                    timestamps = timestamps.append(tempTime, ignore_index = True)
                    team2Count = team2Count + 1
                    timeIndex = (indEvent['timestamp'] // 60000) + 1
                    parsedTimeline.loc[timeIndex, 'team2Dragons'] = team2Count
            if ((indEvent['timestamp'] not in timestamps.values)) and (indEvent["type"] == "ELITE_MONSTER_KILL" and indEvent["monsterType"] == "DRAGON" and indEvent["killerTeamId"] == 100):
                tempTime = pd.Series(indEvent['timestamp'])
                timestamps = timestamps.append(tempTime, ignore_index = True)
                team1Count = team1Count + 1
                timeIndex = (indEvent['timestamp'] // 60000) + 1
                parsedTimeline.loc[timeIndex, 'team1Dragons'] = team1Count
            if ((indEvent['timestamp'] not in timestamps.values)) and (indEvent["type"] == "ELITE_MONSTER_KILL" and indEvent["monsterType"] == "DRAGON" and indEvent["killerTeamId"] == 200):
                tempTime = pd.Series(indEvent['timestamp'])
                timestamps = timestamps.append(tempTime, ignore_index = True)
                team2Count = team2Count + 1
                timeIndex = (indEvent['timestamp'] // 60000) + 1
                parsedTimeline.loc[timeIndex, 'team2Dragons'] = team2Count
            
    parsedTimeline['team1Dragons'] = parsedTimeline['team1Dragons'].ffill(axis = 0)
    parsedTimeline['team2Dragons'] = parsedTimeline['team2Dragons'].ffill(axis = 0)
    parsedTimeline = parsedTimeline.fillna(0)
    return parsedTimeline

def parseTurrets(events, parsedTimeline):
    #Must flip these values
    team1Count = 0
    team2Count = 0
    parsedTimeline['team1Turrets'] = np.nan
    parsedTimeline['team2Turrets'] = np.nan
    timestamps = pd.DataFrame()
    for i in range(len(events)):
        tempEvent = events[i]
        for j in range(len(tempEvent)):
            indEvent = tempEvent[j]
            #attempts to generalize the rectification of double counting events
            if len(timestamps) == 0:
                if (indEvent["type"] == "BUILDING_KILL" and indEvent["buildingType"] == "TOWER_BUILDING" and indEvent["teamId"] == 100):
                    tempTime = pd.Series(indEvent['timestamp'])
                    timestamps = timestamps.append(tempTime, ignore_index = True)
                    team2Count = team2Count + 1
                    timeIndex = (indEvent['timestamp'] // 60000) + 1
                    parsedTimeline.loc[timeIndex, 'team2Turrets'] = team2Count
                if (indEvent["type"] == "BUILDING_KILL" and indEvent["buildingType"] == "TOWER_BUILDING" and indEvent["teamId"] == 200):
                    tempTime = pd.Series(indEvent['timestamp'])
                    timestamps = timestamps.append(tempTime, ignore_index = True)
                    team1Count = team1Count + 1
                    timeIndex = (indEvent['timestamp'] // 60000) + 1
                    parsedTimeline.loc[timeIndex, 'team1Turrets'] = team1Count
            if ((indEvent['timestamp'] not in timestamps.values)) and (indEvent["type"] == "BUILDING_KILL" and indEvent["buildingType"] == "TOWER_BUILDING" and indEvent["teamId"] == 100):
                tempTime = pd.Series(indEvent['timestamp'])
                timestamps = timestamps.append(tempTime, ignore_index = True)
                team2Count = team2Count + 1
                timeIndex = (indEvent['timestamp'] // 60000) + 1
                parsedTimeline.loc[timeIndex, 'team2Turrets'] = team2Count
            if ((indEvent['timestamp'] not in timestamps.values)) and (indEvent["type"] == "BUILDING_KILL" and indEvent["buildingType"] == "TOWER_BUILDING" and indEvent["teamId"] == 200):
                tempTime = pd.Series(indEvent['timestamp'])
                timestamps = timestamps.append(tempTime, ignore_index = True)
                team1Count = team1Count + 1
                timeIndex = (indEvent['timestamp'] // 60000) + 1
                parsedTimeline.loc[timeIndex, 'team1Turrets'] = team1Count
            
    parsedTimeline['team1Turrets'] = parsedTimeline['team1Turrets'].ffill(axis = 0)
    parsedTimeline['team2Turrets'] = parsedTimeline['team2Turrets'].ffill(axis = 0)
    parsedTimeline = parsedTimeline.fillna(0)
    return parsedTimeline
                
#Parse each match for the spent gold, level based on the timestamp
matchInfo = pd.DataFrame(columns = ['timestamp', 'p1.spentGold', 'p1.level', 'p2.spentGold', 'p2.level', 'p3.spentGold', 'p3.level', 'p4.spentGold', 'p4.level', 'p5.spentGold', 'p5.level', 'p6.spentGold', 'p6.level', 'p7.spentGold', 'p7.level', 'p8.spentGold', 'p8.level', 'p9.spentGold', 'p9.level', 'p10.spentGold', 'p10.level', 'team1Dragons', 'team2Dragons', 'team1Turrets', 'team2Turrets', 'team1Win'])
events = pd.DataFrame()
i = 0
for i in range(len(matchIDs)):
    requestURL = ("https://americas.api.riotgames.com/lol/match/v5/matches/" + matchIDs.loc[i] + "/timeline?api_key=" + key)
    timelineRequest = requests.get(requestURL['matchID'])
    timeline = timelineRequest.json()
    timelineInfo = pd.json_normalize(timeline, record_path = ['info', 'frames'])
    timelineEvents = timelineInfo["events"]
    events = timelineEvents.append(timelineInfo["events"], ignore_index = True)
    parsedTimeline = timelineInfo['timestamp']
    winner = events.iloc[-1]
    winner = winner[-1]
    winner = winner['winningTeam']
    for j in range(1, 11):
        timelineInfoTemp = timelineInfo["participantFrames." + str(j) + ".totalGold"]
        timelineInfoTemp = timelineInfoTemp - timelineInfo["participantFrames." + str(j) + ".currentGold"]
        timelineSpent = timelineInfoTemp.rename('p' + str(j) + '.spentGold', axis = 'columns')
        timelineLevel = timelineInfo["participantFrames." + str(j) + ".level"]
        timelineLevel = timelineLevel.rename('p' + str(j) + '.level', axis = 'columns')
        participantGroup = pd.concat([timelineSpent, timelineLevel], axis = 1)
        parsedTimeline = pd.concat([parsedTimeline, participantGroup], axis = 1)
    parsedTimeline = parseDragons(events, parsedTimeline)
    parsedTimeline = parseTurrets(events, parsedTimeline)
    parsedTimeline['team1Win'] = np.nan
    if (winner == 100):
        parsedTimeline = parsedTimeline.fillna(True)
    else:
        parsedTimeline = parsedTimeline.fillna(False)
        
    parsedTimeline = parsedTimeline.drop(parsedTimeline.index[range(5)])
    matchInfo = matchInfo.append(parsedTimeline, ignore_index = True)
    if (i % 5 == 0):
        print("Matches processed: " + str(100*(i/len(matchIDs))) + "%")
        timeRemaining = (len(matchIDs) - i) * 1.5
        print("     Approximately " + str(datetime.timedelta(seconds = timeRemaining)) + " remaining.")
    time.sleep(1.5)