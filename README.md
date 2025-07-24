# Cataphracts Bot

A discord bot containing utilities for assisting with running a game of Sam Sorensen's [Cataphracts](https://samsorensen.blot.im/cataphracts-design-diary-1).

Forked from the [Duck Disciple Bot](https://github.com/Nyhilo/Duck-Disciple-Bot).


## Contributing

Contributions are encouraged. If you do so, please consider using the internal `locale` library to reference strings in the langs/ folder so that this bot may become multilingual in the future.

This repository requires at least python 3.10 and follows [Flake8](https://www.flake8rules.com) formatting standards with a 120 character line length. Please attempt to abide by this, or face reformatting when your time comes.

New commands should be implemented in `cogs/cataphract.py`. That file should be kept to parsing commands from discord only, so all otherwise portable code should go somewhere in `core/`.