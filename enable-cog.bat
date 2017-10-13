@echo off

mklink D:\Red-DiscordBot\cogs\%1.py D:\Scripts\LeGeND-Cogs\%1\%1.py

set source=D:\Red-DiscordBot\data\%1
set target=D:\Scripts\LeGeND-Cogs\%1\data

mklink /d %source% %target%