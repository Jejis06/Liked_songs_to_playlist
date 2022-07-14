import http.server
import time
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys
import numpy as np

#much better and cleanmer than the last one


#statics
redirect_uri = "http://127.0.0.1:8080/"
scopes = "user-library-read playlist-modify-public user-library-modify"
SETTINGS = "./settings.json"
DATABASE = "./data.json"
NAME = "zPolubionych"
DESCRIPTION = ".<>.<>.<>."

#long spaghetti fuunction becouse spotify
def get_tracks_from_playlist(type,obj,pl_id=None):
    if type == "liked":
        t = []
        i = 0
        max = int(obj.current_user_saved_tracks(limit=1)["total"])
        while max:
            x = obj.current_user_saved_tracks(offset=i)["items"]
            for j in x:
                t.append(j["track"]["uri"])
            max -= 20
            i += 20
            if max < 0: break

        return t
    elif type == "ord":
        t = []
        i = 0

        max = int(obj.playlist_tracks(playlist_id=pl_id,limit=1)["total"])
        while max:
            x = obj.playlist_tracks(playlist_id=pl_id,offset=i)["items"]
            for j in x:
                t.append(j["track"]["uri"])
            max -= 100
            i += 100
            if max < 0: break

        return t

def deafult():
    details = {
        "uri":""
    }

    with open(SETTINGS,"w") as f:
        json.dump(details,f,indent=2)
        f.close()

def setup():
    print("------------------> PPtnC-Spotify (setup) <------------------")
    print("This is one time thing, you just have to give me some details and we are done. After setup the program will not ask u to give you credentials if they will be correct")
    print("Here is a quick tutorial how to setup an spotify app 'https://youtu.be/acJUpDNMiik'\nhelpful links : https://developer.spotify.com/dashboard/applications\n")
    client_id = input("Client id:")
    client_secret = input("Client secret:")
    username = input("Username:")

    data = {
        "c_id": client_id,
        "c_s": client_secret,
        "username": username
    }
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=2)
        f.close()

    verify(client_id,client_secret,username)

def verify(client_id,client_secret,username):
    correct = True

    os.environ['SPOTIPY_CLIENT_ID'] = client_id
    os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
    os.environ['SPOTIPY_REDIRECT_URI'] = redirect_uri

    try:
        OAuthtoken = SpotifyOAuth(scope=scopes, username=username)
        obj = spotipy.Spotify(auth_manager=OAuthtoken)
    except :
        correct = False

    if not correct:
        print("Credentials check failed,please set them up right")
        setup()


def main():
    OK = True #ok switch
    try:
        try:
            with open(SETTINGS,"r") as f:
                data = json.load(f)

            URI = data["uri"]

        except:
            deafult()
            with open(SETTINGS,"r") as f:
                data = json.load(f)

            URI = data["uri"]
        if data["uri"] == "":
            OK = False


        #get data from file
        try:
            with open(DATABASE) as f:
                data = json.load(f)

            client_id = data["c_id"]
            client_secret = data["c_s"]
            username = data["username"]
        except:
            setup()
            with open(DATABASE) as f:
                data = json.load(f)

            client_id = data["c_id"]
            client_secret = data["c_s"]
            username = data["username"]


        #set env variables for spotipy
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        os.environ['SPOTIPY_REDIRECT_URI'] = redirect_uri


        #get autorization token
        OAuthtoken = SpotifyOAuth(scope=scopes, username=username)
        obj = spotipy.Spotify(auth_manager=OAuthtoken)


        #create or read playlist for the tracks and get playlist id
        if not OK:
            obj.user_playlist_create(user=username, name=NAME, description=DESCRIPTION, public=True)
            plid = obj.user_playlists(user=username)["items"][0]["id"]

        else:
            plid = URI
            #chack if playlist exists

        #get tracks from playlist and tracks from liked for comparison
        sub_tracks = get_tracks_from_playlist("ord",obj,pl_id=plid)
        upper_tracks = get_tracks_from_playlist("liked",obj)




        # check if playlist is equal to the liked songs and correct if not
        ADDABLE = False
        if len(sub_tracks) == 0:
            ADDABLE = True
        elif (not set(upper_tracks).issubset(set(sub_tracks)) or not set(sub_tracks).issubset(set(upper_tracks))):
            #[*] for slower and less practical solution - lived to show us the better tomorrow
            obj.playlist_remove_all_occurrences_of_items(plid,sub_tracks)
            ADDABLE = True


        if ADDABLE:
            neu = [upper_tracks[i:i + 100] for i in range(0, len(upper_tracks), 100)]
            #print(neu)
            for i in range(len(neu)):
                obj.playlist_add_items(playlist_id=plid, items=neu[i], position=100*i)



        #save uri for flexable playlist name
        if not OK:
            data2 = {
                "uri": f"{plid}"
            }
            with open(SETTINGS, "w") as f:
                json.dump(data2,f,indent=2)
                f.close()
            print(f"Playlist {plid} created")


        #end the program
        else:
            print(f"Playlist {plid} synced")
        return 0

    except :
        return 1


if __name__ == "__main__":
    if main() == 1:
        print("An error happened when running the program")
    input("Press ENter to continue......")


#coded by ignac_pro_69 ;>
