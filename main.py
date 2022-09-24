import json
from dotenv import load_dotenv
import os

from discord.ext import commands
from discord import Intents
from dung import Dung

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.default()

bot = commands.Bot(command_prefix="dung ", intents=intents)
with open('users.json') as f:
    user_data = json.load(f)

bot.add_cog(Dung(bot, user_data))

bot.run(TOKEN)
