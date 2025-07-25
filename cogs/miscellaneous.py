import discord  # noqa: F401
from discord.ext import commands

from core.log import log
from core import nomic_time, sha as shalib, utils, language
from config.config import PREFIX

import d20

locale = language.Locale('cogs.misc')
globalLocale = language.Locale('global')


class Misc(commands.Cog, name='Miscellaneous'):
    '''
    A collection of utility commands that don't really fit in other categories.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='Gets the SHA256 for a given input',
        help=('Gets the SHA256 hash for a given input. Note that including '
              'discord mentions may produce unexpected results.\n'
              'Inputs may be surrounded by double quotes to ensure expected '
              'whitespace.')
    )
    async def sha(self, ctx, *, message=None):
        if message is None:
            await ctx.send(locale.get_string('shaInputMissing'))
            return

        try:
            filteredMessage = utils.trim_quotes(message)
            hash = shalib.get_sha_256(filteredMessage)
            await ctx.send(locale.get_string('shaHashGiven', hash=hash))
        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))

    @commands.command(
        brief='Get unix timestamp for date string',
        help=('Literally just runs the given string against the python-dateutil library. '
              'Can generally be as vague or specific as you want.')
    )
    async def timestamp(self, ctx, *, message=None):
        try:
            timestamp = nomic_time.get_datestring_timestamp(message)
            formattedTimestamp = f'<t:{timestamp}>'
        except Exception:
            return await ctx.send(locale.get_string('timestampBadFormat'))

        await ctx.send(locale.get_string('timestampSuccess',
                                         formattedTimestamp=formattedTimestamp,
                                         timestamp=timestamp))

    @commands.command(
        brief='Roll some dice',
        description='A powerful dice roller',
        help=('Uses the d20 library found at github.com/avrae/d20. '
              'See there for detailed documentation'),
        aliases=['r']
    )
    async def roll(
        self, ctx, *,
        roll=commands.parameter(description='For example: 1d6, 2d6+1d12, 1d20+5, 20d6 >5', default=None)
    ):
        if roll is None:
            return await ctx.send(locale.get_string('rollNone'))

        try:
            r = d20.roll(roll, allow_comments=True)
            chunks = utils.page_message(str(r))
            for chunk in chunks:
                await ctx.send(chunk)

        except d20.RollError as e:
            log.exception(e)
            return await ctx.send(locale.get_string('rollSyntaxError', prefix=PREFIX))

        except d20.RollSyntaxError:
            return await ctx.send(locale.get_string('rollSyntaxError', prefix=PREFIX))

        except d20.RollValueError as e:
            log.exception(e)
            return await ctx.send(locale.get_string('rollSyntaxError', prefix=PREFIX))

        except d20.TooManyRolls:
            return await ctx.send('Ran into a problem, too many rolls.')

        except Exception as e:
            log.exception(e)
            await ctx.send(globalLocale.get_string('genericError'))


async def setup(bot):
    await bot.add_cog(Misc(bot))
