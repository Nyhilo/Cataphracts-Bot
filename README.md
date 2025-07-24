# Cataphracts Bot

A discord bot containing utilities for assisting with running a game of Sam Sorensen's [Cataphracts](https://samsorensen.blot.im/cataphracts-design-diary-1).

Forked from the [Duck Disciple Bot](https://github.com/Nyhilo/Duck-Disciple-Bot).


## Contributing

### Standards

Contributions are encouraged. If you do so, please consider using the internal `locale` library to reference strings in the langs/ folder so that this bot may become multilingual in the future.
```python
locale = language.Locale('some.json.path') # in langs/en-US.json

# ...
async def mycommand(ctx):
    ctx.send(locale.get_string('helloString', audience="World"))
```

This repository requires at least python 3.10 and follows [Flake8](https://www.flake8rules.com) formatting standards with a 120 character line length. Please attempt to abide by this, or face reformatting when your time comes.

New bot commands should be implemented in `cogs/cataphract.py`, which should be reserved for parsing input from discord only.

All program code otherwise should go somewhere in `core/` (such as `core/cataphract.py` to start).

You can test new `core/` code without running the bot by writing test in the `tests/` folder. This repository uses the wonderful [pytest](https://docs.pytest.org/en/stable/) for unit testing. Simply run `pytest tests/{your test file}` and it will run all functions that start with `test_` in that file.

If you add any libraries during your development, please update the requirements.txt using [pipreqs](https://pypi.org/project/pipreqs/).

### Getting Started

To get started with this project, set up a bot for testing on the [discord developer dashboard](https://discord.com/developers/applications/).

On your machine, create a `.env` file in the bot directory.
```
cataphracts-bot/
| .env
| .gitignore
| bot.py
| cogs/
`   ...
```

That file should contain the your test bot token and a debug flag (set to TRUE, if you have code that only runs in debug)
```
TOKEN={your bot token}
DEBUG=TRUE
```

I suggest setting up your bot environment using [venv](https://docs.python.org/3.10/library/venv.html).

Run `pip install -r requirements.txt` to install the required libraries.

Then run `py bot.py` and you should be on your way.
