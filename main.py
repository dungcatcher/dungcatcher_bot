import json
from dotenv import load_dotenv
import os

from discord.ext import commands
from discord import Intents
from dung import Dung
from count import Count

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.default()

bot = commands.Bot(command_prefix="dung ", intents=intents)
cogs = [Dung(bot), Count(bot)]
for cog in cogs:
    bot.add_cog(cog)
bot.run(TOKEN)
