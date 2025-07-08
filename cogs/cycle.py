import discord  # noqa F401
from discord.ext import commands, tasks
import asyncio
import contextlib
from dateutil.parser import ParserError

from core.log import log
from core import nomic_time
from config import config
from config.settings import settings

import core.language as language

globalLocale = language.Locale('global')


class Cycle(commands.Cog, name='Current Cycle'):
    '''
    Commands related to the current Cycle of Infinite Nomic.
    '''

    def __init__(self, bot):
        self.bot = bot

        self.update_khronos.start()

        self.channel_time.start()

    ###########
    # Khronos #
    ###########
    @tasks.loop(minutes=10)
    async def channel_time(self):
        '''
        Sets a datestring as the name of a specific configured voice channel.
        '''
        # Get the current datetime string
        datestring = nomic_time.get_formatted_date_string()

        # Update the channel name
        channel = await self.bot.fetch_channel(config.UTC_UPDATE_CHANNEL)
        await channel.edit(name=datestring)

    @channel_time.before_loop
    async def before_channel_time(self):
        '''
        Delays the start of the time tracking loop until we get to the next 10-minute increment
        '''
        seconds_to_start = nomic_time.seconds_to_next_10_minute_increment()
        log.info(f'Seconds to start tracking time: {seconds_to_start}')
        await asyncio.sleep(seconds_to_start)

    @tasks.loop(count=1)
    async def update_khronos(self):
        '''Run time trackers immediately on start before starting the actual loop'''
        await self.channel_time()


async def setup(bot):
    await bot.add_cog(Cycle(bot))
