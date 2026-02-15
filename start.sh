#!/bin/bash
pip uninstall discord.py discord-components -y
pip install discord.py==2.5.0 --force-reinstall
python bot.py