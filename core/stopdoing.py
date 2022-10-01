import discord

from random import choices, random
from time import sleep
import asyncio
from typing import Callable, List, Union
import re

import config.config as config
from core.log import log


class Option():
    def __init__(self, func: Callable, weight: int, extra_arg: str = None,
                 regexes: Union[str, List[str]] = None):
        """
        An option holds a delegate function so it can be executed later. It also
        allows you to pass an optional additional argument to the delegate.

        :param func:      Delegate function to be executed if this option is
                           chosen
        :param weight:    How many instances of the option are included in the
                           option pool
        :param regex:     Optional regex to match against for arbitrary message
                           replies, defaults to None
        :param extra_arg: An optional additional argument that gets passed to
                           'func' delegate, defaults to None
        """
        self.func = func
        self.weight = weight
        self.extra_arg = extra_arg

        # Let's pre-compile our regexes with case-insensitivity for use later
        if type(regexes) is str:
            regexes = [regexes]

        self.regexes = None if regexes is None else [re.compile(r, re.IGNORECASE) for r in regexes]

    async def execute(self, ctx) -> None:
        """
        Executes the delegate of this option.

        :param ctx: The discord context (usually a "messageable" object) in
                     which to execute this delegate. Used to respond to the
                     triggering message
        """
        if self.extra_arg:
            return await self.func(ctx, self.extra_arg)

        return await self.func(ctx)


class StopDoing():
    def __init__(self, bot) -> None:
        """
        Caches the bot object and options list for use.

        :param bot: _description_
        """
        self.bot = bot
        stop = r'(not|stop(?:ped)?)'
        nomic = rf'{stop} doing nomic'
        punc = r'(?:[\.!?])?'
        pronoun = r'(he|she|they|e)'
        self.options = [
            Option(send_image, 15, 'absolute fools.png', r'absolute fool'),
            Option(send_image, 5, 'become unponderable.png', r'become unponderable'),
            Option(send_image, 10, 'big brain granny.png', r'big brain'),
            Option(send_image, 5, 'birb vs ml.png', rf'{stop} doing (ml|machine learning)'),
            Option(send_image, 5, 'mexican hankerchief.gif', r'kekw'),
            Option(send_image, 15, 'square stop doing nomic.png', nomic),
            Option(send_image, 15, 'stop doing cfjs.png', [nomic, rf'{stop} doing cfj']),
            Option(send_image, 10, 'stop doing math.png', rf'{stop} doing math'),
            Option(send_image, 5, 'stop doing medicine.jpg', rf'{stop} doing medicine'),
            Option(send_image, 10, 'stop doing plantnomic.png', rf'{stop} doing (nomic|plant)'),
            Option(send_image, 10, 'stop doing.png', [rf'stop doing{punc}$', nomic]),
            Option(send_image, 15, 'trungified stop doing.png', nomic),
            Option(send_image, 10, 'you could make a nomic.png',
                   [nomic, r'(could|can) make a nomic out of']),
            Option(send_image, 5, 'stop digging here.png', rf'{stop} digging here'),
            Option(send_image, 10, 'stop driving cars.png', rf'{stop} driving cars'),
            Option(send_image, 5, 'stop doing keyboards.jpg',
                   rf'{stop} (doing|using) (?:mech |mechanical )?(?:key)board'),
            Option(send_image, 10, 'all the players gone.png', [r'dead (game|nomic)', nomic]),
            Option(send_image, 10, 'stop doing stop doing.png', rf'{stop} doing (?:.)?stop doing'),
            Option(send_image, 1, 'stop doing stop doing.png', rf'{stop} doing{punc}$'),
            Option(send_image, 1, 'stop doing2.jpg', [rf'stop doing{punc}', nomic]),
            Option(send_image, 10, 'stop doing logic.jpg', rf'{stop} doing logic'),
            Option(send_image(15, 'stop doing computer science.png', rf'{stop} doing (compsci|computer science)')),
            Option(send_image, 5, 'how can he do this without drowning.jpg',
                   rf'how can {pronoun} do this without drowning'),
            Option(thistbh, 15, None, [nomic, r'this tbh', rf'^this{punc}$']),
            Option(amogus, 10, None, r'^amogus$'),
            Option(bossy, 1),
            Option(downloadupdate, 2, bot)
        ]

    async def choose(self, ctx, msg: str, generic_selection: bool = False) -> None:
        """
        Select a "stop doing" meme and reply to the context with it. Will
        randomly select a result that regex matches the input message if one
        exists, or randomly selects from all options if generic_selection is
        True.

        :param ctx:               The context in which to respond to a trigger
        :param msg:               A message sent by a user that will be matched
        :param generic_selection: Indicates that we should select from all
                                   possible options and that we shouldnot bother
                                   regex-matching, defaults to False
        """
        # This is sincerity protection. Longer messages are more likely to be
        # sincere non-jokes, so we don't want to be a pest in that context
        if not generic_selection and len(msg) > config.STOP_DOING_MSG_LEN_LIMIT:
            return

        # Compile a list of options to choose from later
        options_ = []
        if generic_selection:
            options_ = self.options
        else:
            # Search all options that allow regex matching
            for option in [o for o in self.options if o.regexes is not None]:
                # if an option has multiple matches, any of them can make the option valid
                if any([r.search(msg) for r in option.regexes]):
                    options_.append(option)

        if len(options_) == 0:
            return

        # We have a fixed chance of just posting the usual image
        # explicitly triggering with "stop doing nomic" also overrides the normal weight calculation
        if ((generic_selection or re.search(r'stop(?:ped)? doing nomic', msg.lower()))
                and random() < config.STOP_DOING_DEFAULT_CHANCE):
            response = config.DEFAULT_STOP_DOING_RESPONSE
            log.info('Sending default stopdoing response: {response}')
            return await send_image(ctx, response)

        # If we don't post that one, we select from the option list
        option = choices(
            options_, weights=[option.weight for option in options_])[0]
        log.info(f'Sending stopdoing response: {option.func.__name__}, "{option.extra_arg}"')

        await option.execute(ctx)


####################
# Choice functions #
####################


async def send_image(ctx, filename):
    async with ctx.typing():
        with open(f'{config.SDN_DIR}/{filename}', 'rb') as file:
            f = discord.File(file, filename=filename)

        await ctx.send(file=f)


async def thistbh(ctx):
    await ctx.send('<:thistbh:921574440813346897>')


async def amogus(ctx):
    await ctx.send('ඞ')


async def bossy(ctx):
    await ctx.send('*"Stop doing nomic", "what time is it?", "trungify this '
                   'meme", "pool roll some bullshit".*\n\n'
                   "Don't you all have anything better to do?")


async def downloadupdate(ctx, bot):
    await ctx.send(f'There is an update for {config.PREFIX}stopdoingnomic, '
                   'would you like to download it?')

    yes_list = ['yes', 'ye', 'yeah', 'y']
    no_list = ['no', 'nah', 'nope', 'n']

    def check(m):
        return ((m.channel == ctx or m.channel == ctx.channel) and
                (m.content.lower() in yes_list or m.content.lower() in no_list))

    try:
        response = await bot.wait_for('message', timeout=60, check=check)

        if response.content in no_list:
            sleep(1)
            return await ctx.send('well, fine then. be that way I guess...')

        if response.content in yes_list:
            msg = await ctx.send('Downloading: `[          ]` ')
            sleep(1)
            await msg.edit(content='Downloading: `[||        ]` 20%')
            sleep(2.5)
            await msg.edit(content='Downloading: `[||||      ]` 42%')
            sleep(2.5)
            await msg.edit(content='Downloading: `[|||||||   ]` 69% (nice)')
            sleep(2.5)
            await msg.edit(content='Downloading: `[||||||||| ]` 91%')
            sleep(3)
            await msg.edit(content='Downloading: `[||||||||||]` 96%')
            sleep(4)
            await msg.edit(content='Downloading: `[||||||||||]` 99%')
            sleep(1.5)
            await msg.edit(content='Downloading: `[||||||||||]` 99%.')
            sleep(1.5)
            await msg.edit(content='Downloading: `[||||||||||]` 99%..')
            sleep(1.5)
            await msg.edit(content='Downloading: `[||||||||||]` 99%...')
            sleep(3)
            if random() < .9:
                await msg.edit(content='Downloading: `[||||||||||]` 99%... ERROR')
                sleep(2)
                await ctx.send('shit.')
                sleep(2)
                await ctx.send("uhh... let's just try that again later")
            else:
                await msg.edit(content='Downloading: `[||||||||||]` 100%')
                sleep(2)
                await ctx.send('??? O_o')
                sleep(2)
                await ctx.send('Holy shit it actually worked?? Congrats???')

    except asyncio.TimeoutError:
        await ctx.send("Well fine then. Ignore me why don't you...")
