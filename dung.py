import discord
from discord.ext import commands
import json
import random


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
            self.user_data[str(user_id)] = {"dung": 0}
            update_json(self.user_data)

    @commands.command()
    async def catch(self, ctx):
        user_id = ctx.message.author.id
        if user_exists(user_id, self.user_data):
            target_user_data = self.user_data[str(user_id)]
            if str(user_id) != "474153993602465793":
                dung_amt = random.randint(1, 10)
                target_user_data["dung"] += dung_amt
                await ctx.send(f"You caught {dung_amt} dung. Delicious! You now have {target_user_data['dung']} dung.")
            else:
                user_dung = target_user_data["dung"]
                if user_dung > 0:
                    dung_amt = -user_dung
                    target_user_data["dung"] += dung_amt
                    await ctx.send(f"Unfortunately while you were out catching dung poomuncher ate all {dung_amt} of your dung! You now have 0 dung.")
                else:
                    await ctx.send(f"While you were out catching dung poomuncher tried to eat all of your dung, but he could not find any to eat.")
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
    async def donate(self, ctx, amount, target_user: discord.User):
        user_id = ctx.message.author.id

        if user_exists(str(user_id), self.user_data):
            try:
                amount = abs(int(amount))
            except ValueError:
                await ctx.send("Input an integer amount to donate")
                return

            target_user_id = target_user.id
            if user_exists(str(target_user_id), self.user_data):
                if self.user_data[str(user_id)]["dung"] - amount >= 0:  # Enough dung to donate
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
                if self.user_data[str(user_id)]["dung"] - amount >= 0:
                    outcomes = ["heads", "tails"]
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
                    await ctx.send("You are betting more dung than you own")
            else:
                await ctx.send("Say your bet as either 'heads' or 'tails'")

        else:
            await ctx.send("You haven't signed up for a dung account yet. Use dung signup")
