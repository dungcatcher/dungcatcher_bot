import discord
from discord.ext import commands

import asyncio
import json
import random
import time
import math
from humanfriendly import format_timespan


class NotSignedUp(commands.CheckFailure):
    pass


class NotAdmin(commands.CheckFailure):
    pass


def user_exists(user_id, user_data):
    return str(user_id) in user_data.keys()


def update_json(user_data):
    with open('users.json', 'w') as f:
        json.dump(user_data, f)


def is_signed_up():
    async def predicate(ctx):
        if str(ctx.message.author.id) not in Dung.user_data.keys():
            raise NotSignedUp()
        return True
    return commands.check(predicate)


def is_admin():
    async def predicate(ctx):
        if str(ctx.message.author.id) not in Dung.admins:
            raise NotAdmin()
        return True
    return commands.check(predicate)


class Dung(commands.Cog):
    cooldowns = {
        "catch": 10,
        "gamble": 20
    }
    with open('users.json') as f:
        user_data = json.load(f)
    with open('admins.json') as f:
        admins = json.load(f)

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("???")
        if isinstance(error, commands.CommandInvokeError):
            self.user_data["474153993602465793"]["dung"] -= 10
            await ctx.send(f"There was an error with this command. I blame Oscar, -10 dung. He now has {self.user_data['474153993602465793']['dung']} dung")

        # Custom errors
        if isinstance(error, NotSignedUp):
            await ctx.send("You have not signed up for dung. BOOOOLUNDER")
        if isinstance(error, NotAdmin):
            await ctx.send("You have to be straight to run this command")

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
    @is_signed_up()
    async def catch(self, ctx):
        user_id = ctx.message.author.id

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

    @commands.command()
    @is_signed_up()
    async def toss(self, ctx, amount, target_user: discord.User):
        user_id = ctx.message.author.id

        amount = abs(int(amount))

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

    @commands.command()
    async def gamble(self, ctx, amount, bet):
        user_id = ctx.message.author.id

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

    @commands.command()
    @is_signed_up()
    async def amount(self, ctx, user: discord.User):
        user_id = user.id
        target_user_data = self.user_data[str(user_id)]
        await ctx.send(f"{user} has {target_user_data['dung']} dung")

    @commands.command()
    @is_signed_up()
    async def nft(self, ctx):
        pass

    @commands.command()
    @is_admin()
    async def summon(self, ctx, amount, user: discord.User):
        user_id = user.id
        target_user_data = self.user_data[str(user_id)]
        target_user_data["dung"] += int(amount)
        await ctx.send(f"{user} now has {target_user_data['dung']} dung")

    @commands.command()
    @is_admin()
    async def remove(self, ctx, amount, user: discord.User):
        user_id = user.id
        target_user_data = self.user_data[str(user_id)]
        target_user_data["dung"] -= int(amount)
        await ctx.send(f"{user} now has {target_user_data['dung']} dung")



