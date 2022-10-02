from discord.ext import commands

import time
from humanfriendly import format_timespan
import re
import asyncio
import json


async def scan_channel(channel):
    messages = []

    start = time.time()
    messages += await channel.history(limit=None).flatten()
    elapsed_time = time.time() - start
    print(f"'{channel.name}' scan complete in {format_timespan(elapsed_time)}. Scanned {len(messages)} messages.")

    return messages


class Count(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('admins.json') as f:
            self.admins = json.load(f)

    @commands.command()
    async def update(self, ctx):
        if str(ctx.message.author.id) in self.admins:
            await ctx.send("Updating...")
            start = time.time()
            text_channels = []
            for channel in self.bot.get_guild(741855063764631625).channels:
                if str(channel.type) == 'text':
                    text_channels.append(channel)

            # Asynchronously scans all the text messages
            messages = await asyncio.gather(*[scan_channel(channel) for channel in text_channels])

            message_count_dict = {}
            message_count_leaderboard_dict = {}
            for message in messages:
                if str(message.author) not in message_count_leaderboard_dict.keys():
                    message_count_leaderboard_dict[str(message.author)] = {}

                message_words = re.sub("[^\w]", " ",  message).split()
                message_words = [string for string in message_words if string != ""]  # Remove blank strings

                for word in message_words:
                    if word not in message_count_dict.keys():
                        message_count_dict[word] = 0
                    message_count_dict[word] += 1

                    if word not in message_count_leaderboard_dict[str(message.author)].keys():
                        message_count_leaderboard_dict[str(message.author)][word] = 0
                    message_count_leaderboard_dict[str(message.author)][word] += 1

            with open('message_count.json', 'w') as message_count_file:
                json.dump(message_count_dict, message_count_file)
            with open('message_count_leaderboard.json', 'w') as message_count_leaderboard_file:
                json.dump(message_count_leaderboard_dict, message_count_leaderboard_file)

            await ctx.send(f"Done! That took {format_timespan(time.time() - start)}. Scanned {len(messages)} messages")

    @commands.command()
    async def count(self, ctx, word, lb=None):
        #  Say the amount of times the word has been said
        with open('message_count.json') as message_count_file:
            message_count_data = json.load(message_count_file)
        if word in message_count_data.keys():
            await ctx.send(f"'{word}' has been sent {message_count_data[word]} times{':' if lb else '!'}")
        else:
            await ctx.send(f"'{word}' has never been sent")

        # Show the leaderboard if requested
        if lb == "lb" or lb == "leaderboard":
            with open('message_count_leaderboard.json') as message_count_leaderboard_file:
                message_count_leaderboard_data = json.load(message_count_leaderboard_file)
            lb_msg = ""
            word_lb_dict = {}
            for user_key, user_values in message_count_leaderboard_data.items():
                if word in user_values.keys():
                    word_lb_dict[user_key] = user_values[word]
            if word_lb_dict.keys():  # If anyone has said the word
                word_lb_dict = sorted(word_lb_dict.items(), key=lambda x: x[1], reverse=True)
                rank = 0
                for word_lb_user, word_lb_amt in word_lb_dict:
                    rank += 1
                    lb_msg += f"**{rank}) {word_lb_user}** - {word_lb_amt} times\n"
                    if rank >= 10:
                        break
                await ctx.send(lb_msg)
