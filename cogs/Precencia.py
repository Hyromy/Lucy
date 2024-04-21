import discord, spotipy
from discord.ext import commands, tasks
from steam_web_api import Steam
from spotipy.oauth2 import SpotifyClientCredentials

import random, json
from data.config import STEAM_KEY, STEAM_CLIENT, SPOTIFY_CLIENT, SPOTIFY_SECRET, SPOTIFY_PLAYLIST_ID
class Precencia(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy = Lucy
        self.cooldown = 0
        self.playlist = []
        self.activity = None
        Precencia.__doc__ = "Precencia del bot"
    
    @tasks.loop()
    async def playing(self):
        for i in self.playlist:
            self.activity = discord.Activity(type = discord.ActivityType.listening, name = f"{i["artist"]}, {i["track"]}")
            await self.Lucy.change_presence(activity = self.activity)
            
            self.playing.change_interval(
                minutes = i["duration"]["minutes"],
                seconds = i["duration"]["seconds"])
        else:
            self.playlist.clear()
            self.playing.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        self.newstatus.start()
    
    @tasks.loop()
    async def newstatus(self):
        with open("./data/status.json", encoding = "utf-8") as f:
            data = json.load(f)
        key = random.choice(list(data.keys()))
        
        if key == "🎮":
            client_games = Steam(STEAM_KEY).users.get_owned_games(STEAM_CLIENT)["games"]
            game_list = []
            
            for game in client_games:
                if game["playtime_windows_forever"] >= 60:
                    game_list.append(game["name"])
            
            status = random.choice(game_list)
            self.activity = discord.Game(name = status)
            self.cooldown = 30 + random.randint(0, 30)

        elif key == "🎧":
            client = SpotifyClientCredentials(
                client_id = SPOTIFY_CLIENT,
                client_secret = SPOTIFY_SECRET
            )
            sp = spotipy.Spotify(
                client_credentials_manager = client
            )

            pl_data = sp.playlist(SPOTIFY_PLAYLIST_ID)
            total_playlist = []
            for i in pl_data["tracks"]["items"]:
                track = i["track"]["name"]
                artist = i["track"]["artists"][0]["name"]

                duration_ms = i["track"]["duration_ms"] // 1000
                minutes = duration_ms // 60
                seconds = duration_ms % 60
                duration = {"minutes":minutes, "seconds":seconds}

                total_playlist.append({"track":track, "artist":artist, "duration":duration})

            tracks = random.randint(1, 20)
            i = 0
            while i < tracks:
                song = random.choice(total_playlist)
                if song not in self.playlist:
                    self.playlist.append(song)
                    i += 1

            t_min = 0
            t_sec = 0
            for i in self.playlist:
                t_min += i["duration"]["minutes"]
                t_sec += i["duration"]["seconds"]
            else:
                self.playing.start()
                self.newstatus.change_interval(minutes = t_min, seconds = t_sec)

        elif key == "📺":
            anime = random.choice(data[key])
            self.activity = discord.Activity(type = discord.ActivityType.watching, name = anime)
            self.cooldown = 20 * random.randint(1, 2)

        else:
            status = random.choice(data[key])
            self.activity = discord.CustomActivity(name = f"{key} {status}")
            self.cooldown = random.randint(1, 60)
        
        if key != "🎧":
            await self.Lucy.change_presence(activity = self.activity)
            self.newstatus.change_interval(minutes = self.cooldown)

async def setup(Lucy):
    await Lucy.add_cog(Precencia(Lucy))