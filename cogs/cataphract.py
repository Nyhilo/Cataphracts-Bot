import discord  # noqa F401
from discord.ext import commands

from core.log import log
from config import config

from core import cataphract

import core.language as language
locale = language.Locale('cogs.cataphract')
globalLocale = language.Locale('global')


class Cataphract(commands.Cog, name='Cataphracts'):
    '''
    Commands related to the game of Cataphracts.
    '''

    def __init__(self, bot):
        self.bot = bot

    # @commands.command(
    #     brief='Brief help description',
    #     help=('Long help description.\n'
    #           'With newlines!')
    # )
    # async def mycommand(self, ctx, firstarg, *, fullMessage):
    #     ctx.send(locale.get_string('helloString', audience="World"))   # cogs > cataphract in langs/en-US.json


async def setup(bot):
    await bot.add_cog(Cataphract(bot))
