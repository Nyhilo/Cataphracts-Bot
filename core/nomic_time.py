import discord

from datetime import datetime, timedelta, timezone
import time
import calendar
from dateutil import parser
from dateutil.relativedelta import relativedelta
from math import ceil

from config.settings import settings
from core import language

locale = language.Locale('core.nomic_time') if settings.cycle_running else language.Locale('core.nomic_time_on_break')
print(settings.cycle_running)
print(locale.base_path)


def get_current_utc_string() -> None:
    # Okay there's a lot going on here
    # Get some base reference values
    now = utc_now()

    # Get string representations of the current time and day
    time = now.strftime('%H:%M')
    weekday = now.strftime('%A')

    # Figure out what phase it is
    _phase = _get_phase(now)
    _nextPhase = _phase + 1

    # Get the names of the needed phases
    phase = _get_phase_name(_phase)
    nextPhase = _get_phase_name(_nextPhase)

    # Day of the week for the next phase's beginning
    nextDayDt = _get_date_from_phase(_nextPhase)
    nextDay = nextDayDt.strftime('%A')
    nextDayTimestamp = get_timestamp(nextDayDt)

    # Discord-formatted timestamp strings
    nextDayRelativeTimestampStr = f'<t:{nextDayTimestamp}:R>'
    nextDayTimestampStr = f'<t:{nextDayTimestamp}:F>'

    return locale.get_string(
        'timeUtcReportString',
        time=time,
        weekday=weekday,
        phase=phase,
        nextPhase=nextPhase,
        nextDay=nextDay,
        nextDayRelativeTimestampStr=nextDayRelativeTimestampStr,
        nextDayTimestampStr=nextDayTimestampStr,
    )


#################################
# Phase Determination Functions #
#################################


def _get_phase(date: datetime) -> int:
    '''
    Retrieve the current phase, given the value of utc_now()
    '''
    # This is the total length in days after iterating through all the phases in
    # a "loop" or "group". i.e. [3, 2, 2] is a full week (7 days)
    phase_group_len = sum(settings.current_cycle_phase_loop)

    # This will how phase groups are divided
    num_phases_per_group = len(settings.current_cycle_phase_loop)

    # We want to know how long it's been since we started the cycle.
    days_since_beginning = (date - settings.current_cycle_start_date).days

    # This "rounds down" the days to the most recent full phase group
    # for instance, (20 // 7) * 7 = 18
    phases_since = (
        days_since_beginning // phase_group_len
    ) * num_phases_per_group

    # I don't know why this -1 works, but it fixes an inconsistent off-by-one error
    days_since = (
        (days_since_beginning // phase_group_len) * phase_group_len
    ) - 1

    # Add phases to the running total until we get to today
    for group in settings.current_cycle_phase_loop:
        phases_since += 1
        days_since += group
        if days_since >= days_since_beginning:
            break

    return phases_since


def _get_date_from_phase(phase: int) -> str:
    '''
    Get a datetime for the day that a given phase falls on

    :param phase: _description_
    :return: _description_
    '''
    phases_per_group = len(settings.current_cycle_phase_loop)

    days_since = 0
    count = 0

    # Iterate through the phase lengths until we get to the start day of the phase
    while count < (phase - 1):
        days_since += settings.current_cycle_phase_loop[count % phases_per_group]
        count += 1

    return settings.current_cycle_start_date + relativedelta(days=days_since)


def _get_phase_name(phase: int) -> str:
    phase_names = settings.current_cycle_phase_names

    if phase_names is None or len(phase_names) == 0:
        return "Phase"

    if phase > len(phase_names) - 1:
        return phase_names[-1]

    return phase_names[phase-1]


def _get_week_name(phase: int) -> str:
    weekNum = (phase + 1) // 2
    return locale.get_string('weekName', number=weekNum)


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
    return f'{dayEmoji} {tod}'


def get_current_phase_string():
    '''
    Get the string for the current phase right now.
    '''

    currentPhase = _get_phase(utc_now())

    weekName = _get_week_name(currentPhase)
    phaseName = _get_phase_name(currentPhase)
    return locale.get_string(
        'khronosPhaseString', weekName=weekName, phaseName=phaseName
    )


def get_minutes_to_next_phase() -> int:
    '''
    Get the number of integer minutes to the next phase. This is expected to be
     converted to an HH:MM format so something similar.
    '''
    current_phase = _get_phase(utc_now())
    next_phase_date = _get_date_from_phase(current_phase + 1)
    minutes = (next_phase_date - utc_now()).total_seconds() // 60

    return int(minutes)


def get_next_time_to_phase_end_string():
    minutes = get_minutes_to_next_phase()
    if minutes <= 60:
        return locale.get_string(
            'phaseEndNear', minutes=((minutes // 10) + 1) * 10
        )

    return locale.get_string('phaseEndFar', hours=ceil(minutes / 60))


def seconds_to_next_10_minute_increment():
    '''
    See function name.
    '''
    now = utc_now()
    if now.minute % 10 == 0:
        return 0

    next_minute = ((now.minute // 10) + 1) * 10
    return (next_minute * 60) - ((now.minute * 60) + now.second) + 1


def seconds_to_next_day():
    now = utc_now()

    # Adds 1 day, then replaces the clock time to bring us to 00:00 UTC
    tomorrow = (
        now + relativedelta(days=1) + relativedelta(hour=0, minute=0, second=0)
    )
    return (tomorrow - now).seconds


def set_locale(locale_code: str):
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
