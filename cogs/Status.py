import discord
import random
import os
import asyncio
import spotipy
import json
import datetime

from discord.ext import commands

class Status(commands.Cog):
    def __init__(self, Lucy):
        self.Lucy:commands.Bot = Lucy
        self.activities = ["📺", "🎧"]

        self.spotify = None

    def auth_and_get_playlist(self) -> list[dict]:
        self.spotify = spotipy.Spotify(
            auth_manager = spotipy.oauth2.SpotifyClientCredentials(
                client_id = os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret = os.getenv("SPOTIPY_CLIENT_SECRET"),
                cache_handler = spotipy.cache_handler.CacheFileHandler(
                    cache_path = "spotipyOauthCache.json"
                )
            )
        )

        playlist = self.spotify.playlist_tracks(
            os.getenv("SPOTIPY_PLAYLIST_URL")
        )["items"]
        
        return playlist

    @commands.Cog.listener()
    async def on_ready(self):
        await self.choose_activity()

    async def choose_activity(self):
        activity = random.choice(self.activities)

        if activity == "📺":
            await self.anime()

        elif activity == "🎧":
            await self.music()
        
        await self.choose_activity()

    async def anime(self):
        await self.Lucy.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.watching,
                name = "anime"
            )
        )

        await asyncio.sleep(60)

    async def music(self):
        tracks = []
        tracks_len = random.randint(1, 20)

        playlist_items = self.auth_and_get_playlist()
        while len(tracks) < tracks_len:
            track = random.choice(playlist_items)
            if track not in tracks:
                tracks.append(track)

        for i in range(tracks_len):
            song = tracks[i]["track"]["artists"][0]["name"] + " | "
            song += tracks[i]["track"]["name"]
            album = tracks[i]["track"]["album"]["name"]
            
            await self.Lucy.change_presence(
                activity = discord.Activity(
                    type = discord.ActivityType.listening,
                    name = song,
                    state = "Álbum: " + album
                )
            )

            await asyncio.sleep(tracks[i]["track"]["duration_ms"] / 1000)

async def setup(Lucy):
    await Lucy.add_cog(Status(Lucy))