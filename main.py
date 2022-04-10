import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import time
import pickle
from tqdm import tqdm

client_id = 'your key'
client_secret = 'your  key'
redirect_uri = 'http://localhost:8888'


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope="ugc-image-upload "
                                                     "playlist-modify-private "
                                                     "playlist-read-private "
                                                     "user-read-private "
                                                     "user-read-playback-state "
                                                     "user-library-modify "
                                                     "user-read-playback-position "
                                                     "app-remote-control "
                                                     "user-read-recently-played "
                                                     "user-modify-playback-state "
                                                     "user-read-email "
                                                     "user-follow-modify "
                                                     "playlist-modify-public "
                                                     "user-follow-read "
                                                     "user-read-currently-playing "
                                                     "playlist-read-collaborative "
                                                     "user-library-read "
                                                     "streaming "
                                                     "user-top-read "))

sp_auth = spotipy.oauth2.SpotifyOAuth(client_id = client_id,
                                               client_secret = client_secret,
                                               redirect_uri = redirect_uri,
                                               scope = "ugc-image-upload "
                                                       "playlist-modify-private "
                                                       "playlist-read-private "
                                                       "user-read-private "
                                                       "user-read-playback-state "
                                                       "user-library-modify "
                                                       "user-read-playback-position "
                                                       "app-remote-control "
                                                       "user-read-recently-played "
                                                       "user-modify-playback-state "
                                                       "user-read-email "
                                                       "user-follow-modify "
                                                       "playlist-modify-public "
                                                       "user-follow-read "
                                                       "user-read-currently-playing "
                                                       "playlist-read-collaborative "
                                                       "user-library-read "
                                                       "streaming "
                                                       "user-top-read ")

sp.currently_playing()
auth_token =sp_auth.get_cached_token()
auth_token = "Bearer " + str(auth_token['access_token'])
username = sp.me()["id"]


# ======================================================================================================================
# 1/5 get song data
# ======================================================================================================================
artists = []
count = 0

url = "https://api.spotify.com/v1/me/tracks?limit=10&offset=5"

# data = requests.get(url, headers={'Authorization': auth_token})
data = requests.get(url, headers={'Authorization': auth_token}).json()
num_of_tracks = data['total']

pbar0 = tqdm(total=num_of_tracks)
pbar0.set_description("1/5 Get song data")

while 1 == 1:
    url = "https://api.spotify.com/v1/me/tracks?limit=50&offset=" + str(count)
    data = requests.get(url, headers={'Authorization': auth_token}).json()
    num_of_tracks = data['total']

    find = range(0, 50)
    for i in find:
        pbar0.update(1)
        try:
            iner_list = []
            iner_list.append(data['items'][i]['track']['name'])  # song name
            iner_list.append(data['items'][i]['track']['external_urls']['spotify'])  # song url
            iner_list.append(data['items'][i]['track']['artists'][0]['name'])  # artist name
            iner_list.append(data['items'][i]['track']['artists'][0]['external_urls']['spotify'])  # artist url

            url = "https://api.spotify.com/v1/artists/" + data['items'][i]['track']['artists'][0]['id']  # get genres
            pog = requests.get(url, headers={'Authorization': auth_token}).json()
            iner_list.append(pog["genres"])

            artists.append(iner_list)
        except:
            pass

    count += 50
    if count > int(num_of_tracks):
        break

pbar0.close()

# ======================================================================================================================
# 2/5 get genre list
# ======================================================================================================================

pbar1 = tqdm(total=num_of_tracks)
pbar1.set_description("2/5 get genre list")

genre_list = []

for x in artists:
    pbar1.update(1)
    for z in x[4]:
        if not z in genre_list:
            genre_list.append(z)

pbar1.update(1)
pbar1.close()

# ======================================================================================================================
# 3/5 get playlist data
# ======================================================================================================================

current_playlist = sp.user_playlists(username, offset=count)
total_playlists = current_playlist['total']

pbar2 = tqdm(total=total_playlists)
pbar2.set_description('3/5 get playlist data')

current_playlist_names = []
current_playlist_id = []
playlist_data = []
count = 0

def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    data = []
    for x in tracks:
        try:
            data.append(x['track']['name'])  # song name)
        except:
            pass

    if data != []:
        return data
    else:
        return "No songs in playlist"


while True:
    current_playlist = sp.user_playlists(username, offset=count)
    for x in current_playlist['items']:
        inter_list = []
        inter_list.append(x['name'])
        inter_list.append(x['id'])
        inter_list.append(get_playlist_tracks(username, x['id']))
        playlist_data.append(inter_list)
        count += 1
        pbar2.update(1)
    if (count >= total_playlists):
        break

# ======================================================================================================================
# 4/5 make playlists
# ======================================================================================================================

pbar3 = tqdm(total=len(genre_list))
pbar3.set_description('4/5 make playlists')

play_names = []
for x in playlist_data:
    play_names.append(x[0])

x = ""
for x in genre_list:
    pbar3.update(1)
    name = x + '_code'
    if name not in play_names:
        sp.user_playlist_create(username, name=name)
    else:
        # print(name + " already exists")
        pass

pbar3.close()

# ======================================================================================================================
# 5/5 add songs to playlists
# ======================================================================================================================

pbar4 = tqdm(total=num_of_tracks)
pbar4.set_description('5/5 add songs to playlists')

not_in_playlist = []
count = 0
for x in artists:
    pbar4.update(1)
    for z in x[4]:
        playlist_name = z + "_code"
        for y in playlist_data:
            if playlist_name == y[0]:
                if x[0] not in y[2]:
                    sp.user_playlist_add_tracks(username, y[1], [x[1]])
pbar4.update(1)

pbar4.close()