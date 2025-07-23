import discord

from datetime import datetime, timedelta, timezone
import time
import calendar
from dateutil import parser
from dateutil.relativedelta import relativedelta

from core import language

locale = language.Locale('core.nomic_time')


################################
# Scheduling Related Utilities #
################################


def get_formatted_date_string(timestamp: int = None) -> str:
    '''
    Gets a formatted datestring for the given timestamp. Returns the time string
     for the current time if no timestamp is given.

    :param timestamp: UTC timestamp, defaults to None
    :return: Formatted datetime string
    '''
    dt = None
    if timestamp is None:
        istTimeOffset = -14
        dt = utc_now() + timedelta(hours=istTimeOffset)
    else:
        dt = get_datetime(timestamp)

    dayEmoji = '☀️' if dt.hour >= 6 and dt.hour < 18 else get_moon_phase(dt)
    tod = get_diagetic_tod(dt)
    return locale.get_string('formattedTime', timeOfDayEmoji=dayEmoji, time=tod)


def seconds_to_next_10_minute_increment():
    '''
    See function name.
    '''
    now = utc_now()
    if now.minute % 10 == 0:
        return 0

    next_minute = ((now.minute // 10) + 1) * 10
    return (next_minute * 60) - ((now.minute * 60) + now.second) + 1


def set_locale(locale_code: str):
    '''
    Currently unused, but could be used to change the language of functions in this file.
    '''
    global locale
    locale = language.Locale(locale_code)


#####################
# General Utilities #
#####################


def utc_now() -> datetime:
    # for debugging
    # return datetime(month=10, day=21, year=2022, hour=0, minute=59, second=1).replace(tzinfo=timezone.utc)

    return discord.utils.utcnow()


def unix_now():
    '''Returns the current unix timestamp in seconds.'''
    return int(time.time())


def parse_timespan_by_units(number, unit):
    if unit.lower().startswith('sec'):
        return timedelta(seconds=number)

    if unit.lower().startswith('min'):
        return timedelta(minutes=number)

    if unit.lower().startswith('hour'):
        return timedelta(hours=number)

    if unit.lower().startswith('day'):
        return timedelta(days=number)

    if unit.lower().startswith('week'):
        return timedelta(weeks=number)

    return None


def get_full_days_ago(days: int) -> datetime:
    '''Returns a datetime set to the 00:00 of the day 7 days prior.'''

    return (utc_now() - relativedelta(days=days)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def get_moon_phase(date: datetime):
    moonPhases = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
    phaseCount = len(moonPhases)
    moonCyclePeriod = 29.53058867
    offset = (moonCyclePeriod / phaseCount) / 2

    referenceNewMoon = datetime(2025, 1, 29, tzinfo=timezone.utc)
    daysSinceReference = (date - referenceNewMoon).days + offset
    daysSinceNewMoon = (daysSinceReference % moonCyclePeriod)
    phaseIndex = int((daysSinceNewMoon * phaseCount) // moonCyclePeriod)

    return moonPhases[phaseIndex]


def get_diagetic_tod(date: datetime):
    tods = [
            'Midnight',         # 11 - 1am
            'Past Midnight',    # 1 - 3am
            'Before Dawn',      # 3 - 5am

            'Dawn',             # 5 - 7am
            'Early Morning',    # 7 - 9am
            'Morning',          # 9 - 11am

            'Noon',             # 11 - 1pm
            'Afternoon',        # 1 - 3pm
            'Late Afternoon',   # 3 - 5pm

            'Dusk',             # 5 - 7pm
            'Evening',          # 7 - 9pm
            'Late Evening',     # 9 - 11pm
            ]
    hour = 0 if date.hour == 23 else date.hour + 1
    index = int(hour / (24/len(tods)))
    return tods[index]


######################
# Timstamp Utilities #
######################


def get_timespan_from_timestamp(timestamp, now=None):
    if not now:
        now = utc_now()

    return datetime.utcfromtimestamp(timestamp).replace(
        tzinfo=timezone.utc
    ) - now.replace(tzinfo=timezone.utc)


def get_datestring_timestamp(datestring: str) -> int:
    if datestring is None or datestring == '' or datestring.lower() == 'now':
        return unix_now()

    return get_timestamp(parser.parse(datestring))


def get_timestamp(date: datetime) -> int:
    return int(calendar.timegm(date.utctimetuple()))


def get_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, timezone.utc)


def get_datestring_datetime(datestring: str) -> datetime:
    return get_datetime(get_datestring_timestamp(datestring))
