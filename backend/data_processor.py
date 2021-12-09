import numpy as np
import pandas as pd
import json
import random

from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

#import matplotlib.pyplot as plt

##!pip install kneed
from kneed import KneeLocator
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
from sklearn import preprocessing

columns = ["name", \
           "artist", \
           "danceability",\
           "energy",\
           "key",\
           "loudness",\
           "mode",\
           "speechiness",\
           "acousticness",\
           "instrumentalness",\
           "liveness",\
           "valence",\
           "tempo",\
           "uri",\
           "duration_ms",\
           "time_signature",
           "from_id"]

def filterTrack(track):
    features = track['features']

    name = track['track']['name']
    artist = track['track']['artists'][0]['name']
    danceability = features['danceability']
    energy = features['energy']
    key = features['key']
    loudness = features['loudness']
    mode = features['mode']
    speechiness = features['speechiness']
    acousticness = features['acousticness']
    instrumentalness = features['instrumentalness']
    liveness = features['liveness']
    valence = features['valence']
    tempo = features['tempo']
    uri = features['uri']
    duration_ms = features['duration_ms']
    time_signature  = features['time_signature']
    from_id = track['from_id']

    return (name, artist, danceability,energy,key,loudness,mode,speechiness,acousticness,instrumentalness,liveness,valence,tempo,uri,duration_ms,time_signature,from_id)

def jsonToPandas(json_tracks):
    filtered = [track for track in map(filterTrack, json_tracks['allTracks'])]

    return pd.DataFrame(np.array(filtered), columns=columns)

#assign scores to a user's songs based on the ranking order
#example: if there is a top 50, the first song in the ranking receives a score 50/50 = 1, the second song a score 49/50 = 0.98, and so on
def calculateScores(df):
    users = df['from_id'].unique()
    scores = np.zeros(df.shape[0])
    idx = 0
    for user in users:
        user_songs = df[df['from_id'] == user]
        l = user_songs.shape[0]
        user_scores = np.arange(l, 0, -1) / l
        scores[idx: idx + l] = user_scores
        idx += l
    df['score'] = scores

    return df

# This function finds duplicate songs, and creates only one tuple, summing the
# score given by each user and creating a list of the user names
def treatDuplicateSongs(df):
    dup = df['uri'].value_counts().to_frame()
    dups = set(dup[dup['uri'] > 1].index)

    for dup_track in dups:
        duplicate_track_indices = df['uri'] == dup_track
      
        dup_users = df[duplicate_track_indices]['from_id']
        dup_scores = df[duplicate_track_indices]['score']
        
        base_track = df[duplicate_track_indices].iloc[0]
        base_track['from_id'] = ';'.join(dup_users) # Adding all the users
        base_track['score'] = dup_scores.sum()
        
        df = df[~duplicate_track_indices]
        df = df.append(base_track, ignore_index=True)

    return df

"""
clustering models and so on
"""

#given the labels, separate in groups using the dataframe
def separateGroups(completeTable, labels, k):
    n = len(labels)
    groups = [None] * k

    for i in range(n):
        if (groups[labels[i]] == None):
            groups[labels[i]] = []

        groups[labels[i]].append(completeTable.iloc[i])
    
    return groups

#sort the songs in the group by the score
def sortGroups(groups):
    for group in groups:
        random.shuffle(group) #to select songs with equal score in a random way
        group.sort(reverse = True, key = lambda song: song['score'])

#count the quantity of people represented by each group and the weight is the quantity of people/total population in clusters
def calculateWeight(groups):
    groupsQuantPeople = []
    total = 0
    for group in groups:
        people = set()
        for song in group:
            people.update(song['from_id'].split(';')) #the column people
        groupsQuantPeople.append(len(people))
        total += len(people)
    
    for i in range(len(groups)):
        groups[i].append(groupsQuantPeople[i]/total)

#select weight * number of songs in the playlist songs from each group
#if the number of songs is less than the group has, give it to the next more representative group
def mountPlaylist(groups, numSongs):
    remainingSongs = 0
    playlist = []

    #SORT BY WEIGHT
    groups.sort(reverse = True, key = lambda group: group[-1])

    for group in groups:
        n = len(group) - 1 #because of the column weight
        selectedSongs = int(group[-1] * numSongs) + remainingSongs
        if (selectedSongs > n):
            remainingSongs = selectedSongs - n
            playlist.extend(group[i]['uri'] for i in range(n))
            #playlist.extend(group[:n]) #the column URI
        else:
            playlist.extend(group[i]['uri'] for i in range(selectedSongs))
            #playlist.extend(group[:selectedSongs])
    
    return playlist

"""
Playlist generator
"""

#execute the elbow method to choose the best number of clusters to kmeans algorithm
def elbowMethod(features):
    kmeans_kwargs = {
            "init": "random",
            "n_init": 10,
            "max_iter": 300,
            "random_state": 42,
    }

    # A list holds the SSE values for each k
    sse = []
    for k in range(1, 11):
            kmeans = KMeans(n_clusters = k, **kmeans_kwargs)
            kmeans.fit(features)
            sse.append(kmeans.inertia_)

    kl = KneeLocator(
        range(1, 11), sse, curve="convex", direction="decreasing"
    )

    return kl.elbow

#executes kmeans to separe in clusters and mount a playlist
def generatePlaylist(df, features, numSongs):
    numClusters = elbowMethod(features)

    #initiliazing the algorithm
    kmeans = KMeans(
        init="k-means++",
        n_clusters=numClusters,
        n_init=10, #as various runs can give different results, do some runs and choose the one with the lowest SSE
        max_iter=300,
    )

    kmeans.fit_predict(features)
    labels = kmeans.labels_
    df['cluster'] = labels

    groups = separateGroups(df, labels, numClusters)
    sortGroups(groups)
    calculateWeight(groups)
    playlist = mountPlaylist(groups, numSongs)

    return playlist

def runGeneratePlaylist(jsonInfo):
    df = jsonToPandas(jsonInfo)
    df = calculateScores(df)
    df = treatDuplicateSongs(df)

    scaled_features = df.loc[:, ["danceability", "energy", "valence"]]
    return generatePlaylist(df, scaled_features, 50)

if __name__ == '__main__':
    import sys

    l = runGeneratePlaylist(json.loads(open(sys.argv[1]).read()))
    print(l)
