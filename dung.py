import discord
from discord.ext import commands

import asyncio
import json
import random
import time
import math
import os
import string
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
        with open('nfts.json') as f:
            self.nfts = json.load(f)
        self.update_nfts()

    def update_nfts(self):
        files = os.listdir('./nfts')
        for file in files:
            file_found = False
            for nft_data in self.nfts.values():
                if nft_data['name'] == file:
                    file_found = True

            if not file_found:
                file_hash = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))  # 8 digit random string

                nft = {'sold_to': None, 'name': file}
                self.nfts[file_hash] = nft

        with open('nfts.json', 'w') as f:
            json.dump(self.nfts, f)

        print(self.nfts)

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
            raise error
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('More arguments required')

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
    async def nft(self, ctx, mode, choice=None):
        if mode == 'shop':
            msg = ""
            for nft_hash, nft_data in self.nfts.items():
                msg_line = f"**{nft_hash}**: *{nft_data['name']}*"
                if nft_data['sold_to']:
                    user_bought = await self.bot.fetch_user(nft_data['sold_to'])
                    msg_line = '~~' + msg_line + '~~'  # Strikeout
                    msg_line += f' **Sold to {user_bought}**'
                msg_line += '\n'
                msg += msg_line
            await ctx.send('Welcome to dung NFTs, the home of normal images of Oscar assaulting minors:')
            await ctx.send(msg)
        elif mode == 'buy':
            if choice:
                if choice in self.nfts.keys():
                    if not self.nfts[choice]['sold_to']:
                        if self.user_data[str(ctx.message.author.id)]['dung'] - 100 >= 0:
                            await ctx.send(f"Thank you for purchasing *{self.nfts[choice]['name']}*. Your image will arrive in "
                                           "your DMs shortly. -100 dung")
                            self.user_data[str(ctx.message.author.id)]['dung'] -= 100
                            self.nfts[choice]['sold_to'] = ctx.message.author.id

                            user = await self.bot.fetch_user(ctx.message.author.id)
                            await user.send('😁😁😁 Well done! 😁😁😁')
                            await user.send(f"You now own *{self.nfts[choice]['name']}*!")

                            with open(f'./nfts/{self.nfts[choice]["name"]}', 'rb') as f:
                                picture = discord.File(f)
                            await user.send(file=picture)
                            # Save
                            with open('nfts.json', 'w') as f:
                                json.dump(self.nfts, f)
                        else:
                            await ctx.send("You don't have enough dung for this purchase")
                    else:
                        await ctx.send(f"This NFT has already been bought by {await self.bot.fetch_user(self.nfts[choice]['sold_to'])}")
                else:
                    ctx.send("That NFT doesn't exist")
            else:
                raise commands.MissingRequiredArgument(choice)
        else:
            raise commands.CommandNotFound()

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



