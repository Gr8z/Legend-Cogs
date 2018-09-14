@echo off

mklink C:\Scripts\Red-DiscordBot\cogs\%1.py C:\Scripts\LeGeND-Cogs\%1\%1.py

set source=C:\Scripts\Red-DiscordBot\data\%1
set target=C:\Scripts\LeGeND-Cogs\%1\data

mklink /d %source% %target%