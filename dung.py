import discord
from discord.ext import commands

import json
import random
import time
import math
from humanfriendly import format_timespan
import re


def user_exists(user_id, user_data):
    return str(user_id) in user_data.keys()


def update_json(user_data):
    with open('users.json', 'w') as f:
        json.dump(user_data, f)


class Dung(commands.Cog):
    def __init__(self, bot, user_data):
        self.bot = bot
        self.user_data = user_data
        self.admins = ["604252516527636482"]
        self.cooldowns = {
            "catch": 10,
            "gamble": 20
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')

    @commands.command()
    async def signup(self, ctx):
        user_id = ctx.message.author.id
        if user_exists(user_id, self.user_data):
            await ctx.send("You have already signed up!")
        else:
            await ctx.send("Thank for for signing up for dung!")
            self.user_data[str(user_id)] = {
                "dung": 0,
                "cooldowns":
                {
                    "catch": 0,
                    "gamble": 0
                }
            }
            update_json(self.user_data)

    @commands.command()
    async def catch(self, ctx):
        user_id = ctx.message.author.id
        if user_exists(user_id, self.user_data):  # User has signed up
            target_user_data = self.user_data[str(user_id)]
            elapsed_time = time.time() - target_user_data["cooldowns"]["catch"]
            if elapsed_time >= self.cooldowns["catch"]:  # Command can be run
                if str(user_id) != "474153993602465793":  # Not oscar
                    dung_amt = random.randint(1, 10)
                    target_user_data["dung"] += dung_amt
                    await ctx.send(f"You caught {dung_amt} dung. Delicious! You now have {target_user_data['dung']} dung.")
                else:
                    user_dung = target_user_data["dung"]
                    if user_dung > 0:
                        target_user_data["dung"] -= user_dung
                        await ctx.send(f"Unfortunately while you were out catching dung poomuncher ate all {user_dung} of your dung! You now have 0 dung.")
                    else:
                        await ctx.send(f"While you were out catching dung poomuncher tried to eat all of your dung, but he could not find any to eat.")
                target_user_data["cooldowns"]["catch"] = time.time()  # Update timestamp
            else:
                await ctx.send(f"Please wait {format_timespan(math.ceil(self.cooldowns['catch'] - elapsed_time))} before catching more dung")

            update_json(self.user_data)
        else:
            await ctx.send("You haven't signed up for a dung account yet. Use dung signup")

    @commands.command()
    async def amount(self, ctx, user: discord.User):
        user_id = user.id
        if user_exists(user_id, self.user_data):
            target_user_data = self.user_data[str(user_id)]
            await ctx.send(f"{user} has {target_user_data['dung']} dung")

    @commands.command()
    async def toss(self, ctx, amount, target_user: discord.User):
        user_id = ctx.message.author.id

        if user_exists(str(user_id), self.user_data):
            try:
                amount = abs(int(amount))
            except ValueError:
                await ctx.send("Input an integer amount to toss")
                return

            target_user_id = target_user.id
            if user_exists(str(target_user_id), self.user_data):
                if self.user_data[str(user_id)]["dung"] - amount >= 0:  # Enough dung to toss
                    self.user_data[str(user_id)]["dung"] -= amount
                    self.user_data[str(target_user_id)]["dung"] += amount
                    update_json(self.user_data)

                    await ctx.send(f"You now have {self.user_data[str(user_id)]['dung']} and {target_user} has "
                                   f"{self.user_data[str(target_user_id)]['dung']}")

                else:
                    await ctx.send("You don't have enough dung to do that")
            else:
                await ctx.send("This user has not signed up for dung. BOOOOLUNDER")
        else:
            await ctx.send("You haven't signed up for a dung account yet. Use dung signup")

    @commands.command()
    async def gamble(self, ctx, amount, bet):
        user_id = ctx.message.author.id

        if user_exists(str(user_id), self.user_data):
            try:
                amount = abs(int(amount))
            except ValueError:
                await ctx.send("Input an integer amount to bet")
                return

            if bet == "heads" or bet == "tails":
                if self.user_data[str(user_id)]["dung"] - amount >= 0:  # Enough dung
                    elapsed_time = time.time() - self.user_data[str(user_id)]["cooldowns"]["gamble"]
                    if elapsed_time >= self.cooldowns["gamble"]:
                        self.user_data[str(user_id)]["cooldowns"]["gamble"] = time.time()
                        if str(user_id) in self.admins:  # Admins are just very lucky
                            await ctx.send(f"I have flipped a coin. It was {bet}")
                            self.user_data[str(user_id)]["dung"] += amount
                            update_json(self.user_data)
                            await ctx.send(f"Well done. You won {amount} dung! You now have {self.user_data[str(user_id)]['dung']} dung")
                        else:  # Others have a 33% chance of winning
                            random_num = random.randint(1, 3)
                            if random_num == 2:  # 33% chance
                                await ctx.send(f"I have flipped a coin. It was {bet}")
                                self.user_data[str(user_id)]["dung"] += amount
                                update_json(self.user_data)
                                await ctx.send(f"Well done. You won {amount} dung! You now have {self.user_data[str(user_id)]['dung']} dung")
                            if random_num != 2 or str(user_id) == "474153993602465793":  # Or if it is oscar
                                scam_result = "heads" if bet == "tails" else "tails"
                                await ctx.send(f"I have flipped a coin. It was {scam_result}")
                                self.user_data[str(user_id)]["dung"] -= amount
                                update_json(self.user_data)
                                await ctx.send(f"L you lost. You lost {amount} dung! You now have {self.user_data[str(user_id)]['dung']} dung")
                    else:
                        await ctx.send(f"Please wait {format_timespan(math.ceil(self.cooldowns['gamble'] - elapsed_time))} before gambling your dung")
                else:
                    await ctx.send("You are betting more dung than you own")
            else:
                await ctx.send("Say your bet as either 'heads' or 'tails'")

        else:
            await ctx.send("You haven't signed up for a dung account yet. Use dung signup")

    @commands.command()
    async def update(self, ctx):
        if str(ctx.message.author.id) in self.admins:
            await ctx.send("Updating...")
            start = time.time()
            text_channels = []
            for channel in self.bot.get_guild(741855063764631625).channels:
                if str(channel.type) == 'text':
                    text_channels.append(channel)

            messages = []
            for channel in text_channels:
                channel_start = time.time()
                channel_messages = await channel.history(limit=None).flatten()
                messages += channel_messages
                await ctx.send(f"'{channel.name}' scan complete in {format_timespan(time.time() - channel_start)}. Scanned {len(channel_messages)} messages.")
                print(f"{len(messages)} messages scanned")

            message_count_dict = {}
            message_count_leaderboard_dict = {}
            for message in messages:
                if str(message.author) not in message_count_leaderboard_dict.keys():
                    message_count_leaderboard_dict[str(message.author)] = {}

                message_words = re.sub("[^\w]", " ", message.content).split()  # Get all words
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