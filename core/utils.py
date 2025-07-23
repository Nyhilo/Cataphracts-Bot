from config.config import GLOBAL_ADMIN_IDS, SERVER_ADMIN_IDS, MESSAGE_LIMIT, LINE_SPLIT_LIMIT


def trim_quotes(string):
    # check if the string is surrounded by quotes
    if string[0] == '"' and string[-1] == '"':
        return string[1:-1]

    return string


def strip_command(message, command):
    '''
    Strip the leading command word off a message, if it's there.
    '''
    if not message.startswith(command):
        return message

    return ' '.join(message.split(' ')[1:])


def is_admin(userId, serverId=None):
    if userId in GLOBAL_ADMIN_IDS:
        return True

    if not serverId or serverId not in SERVER_ADMIN_IDS:
        return False

    return userId in SERVER_ADMIN_IDS[serverId]


def roman_numeralize(num):
    '''
    Stolen and modified from w3resource.com
    '''
    if num == 0:
        return '0'

    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC",
           "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


def page_message(message: str, limit: int = MESSAGE_LIMIT, line_split_limit: int = LINE_SPLIT_LIMIT) -> list[str]:
    if len(message) <= limit:
        return [message]

    limit = limit - 6   # Buffer for codeblocks

    result = []
    buffer = ''

    while len(message) > 0 and message != '```':
        if len(message) < limit:
            if message.count('```') % 2 == 1:    # Search for unclosed codeblocks
                message += '```'

            result.append(message)
            break

        buffer = message[:limit]

        newline = buffer.rfind('\n')
        if newline != -1 and newline > (limit - line_split_limit):
            buffer = buffer[:newline]
            message = message[newline:].lstrip('\n')

            if buffer.count('```') % 2 == 1:    # Search for unclosed codeblocks
                buffer += '```'
                message = '```' + message

            result.append(buffer)
            continue

        space = buffer.rfind(' ')

        if space != -1 and space > (limit - line_split_limit):
            buffer = buffer[:space]
            message = message[space:].lstrip()

            if buffer.count('```') % 2 == 1:    # Search for unclosed codeblocks
                buffer += '```'
                message = '```' + message

            result.append(buffer)
            continue

        message = message[limit:]
        if buffer.count('```') % 2 == 1:    # Search for unclosed codeblocks
            buffer += '```'
            message = '```' + message

        result.append(buffer)

    return result
