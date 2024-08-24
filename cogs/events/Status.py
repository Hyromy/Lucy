import discord
import random
import os
import asyncio
import spotipy
import animeflv
import steam_web_api

import common.activies

from discord.ext import commands
class Status(commands.Cog):
    def __init__(self, Lucy:commands.Bot):
        self.Lucy = Lucy
        self.activities = ["📺", "🎧", "🎮", "✏️"]
        self.description = "Estados de Lucy"

    def auth_and_get_playlist(self) -> list[dict]:
        sp = spotipy.Spotify(
            auth_manager = spotipy.oauth2.SpotifyClientCredentials(
                client_id = os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret = os.getenv("SPOTIPY_CLIENT_SECRET"),
                cache_handler = spotipy.cache_handler.CacheFileHandler(
                    cache_path = "spotipyoauthcache.cache"
                )
            )
        )

        playlist = sp.playlist_tracks(
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

        elif activity == "🎮":
            await self.game()

        elif activity == "✏️":
            await self.custom()

        await self.choose_activity()

    async def anime(self):
        intents = 0
        animes = []
        while not animes and intents < 10:
            with animeflv.AnimeFLV() as af:
                animes = af.get_latest_animes()
        
            if not animes:
                intents += 1

            else:
                for _ in range(random.randint(1, 3)):
                    anime = random.choice(animes)
                    await self.Lucy.change_presence(
                        activity = discord.Activity(
                            type = discord.ActivityType.watching,
                            name = anime.title,
                        )
                    )
                    await asyncio.sleep(random.randint(1200, 1440))

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

    async def game(self):
        steam = steam_web_api.Steam(os.getenv("STEAM_API_KEY"))
        user_games = steam.users.get_owned_games(os.getenv("STEAM_USER_ID"))["games"]

        game_list = []
        for game in user_games:
            if game["playtime_forever"] > 60:
                game_list.append(game)

        game = random.choice(game_list)
        await self.Lucy.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.playing,
                name = game["name"],
            )
        )
        await asyncio.sleep(random.randint(600, 3600))

    async def custom(self):
        data = common.activies.read_json_file("./common/status")
        emoji = random.choice(list(data.keys()))
        status = random.choices(data[emoji])[0]

        await self.Lucy.change_presence(
            activity = discord.CustomActivity(
                name = f"{emoji} {status}"
            )
        )
        await asyncio.sleep(random.randint(300, 3600))

async def setup(Lucy:commands.Bot):
    await Lucy.add_cog(Status(Lucy))