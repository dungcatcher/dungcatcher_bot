from discord.ext import commands
from discord import Intents
import json
from dung import Dung

intents = Intents.default()

bot = commands.Bot(command_prefix="dung ", intents=intents)
with open('users.json') as f:
    user_data = json.load(f)

bot.add_cog(Dung(bot, user_data))

TOKEN = 'NzExNzIxNzk5NjE1Nzc0NzIw.GsWk-0.yrXYB6DnE1BqhRUlRGciq89GL9U9p1kNPo9xEs'
bot.run(TOKEN)
