import discord
from discord.ext import commands
import ast
import requests
import subprocess
import psutil
import os
import asyncio
import traceback
import sys
import random

current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the project directory
project_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Add the project directory to sys.path
sys.path.insert(0, project_dir)

import app.settings

token = app.settings.DISCORD_BOT_TOKEN

intents = discord.Intents.default()
intents.message_content = True

allowed_user_ids = [360808288578830336]

def nigger(ctx):
    return ctx.author.id in allowed_user_ids

def insert_returns(body):
  if isinstance(body[-1], ast.Expr):
      body[-1] = ast.Return(body[-1].value)
      ast.fix_missing_locations(body[-1])
  
  if isinstance(body[-1], ast.If):
      insert_returns(body[-1].body)
      insert_returns(body[-1].orelse)
  
  if isinstance(body[-1], ast.With):
      insert_returns(body[-1].body)

bot = commands.Bot(command_prefix='~', intents=intents)

responses = ["1", "2", "3", "4", "5"]

@bot.command()
@commands.check(nigger)
async def eval(ctx, *, cmd):
    """Evaluates input."""
    fn_name = "_eval_expr"

    cmd = cmd.strip("`py ")

    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

    body = f"async def {fn_name}(ctx, env): \n{cmd}"

    try:
        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        local_vars = {}

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__,
            'requests': requests,
            'subprocess': subprocess,
            'psutil': psutil,
            'os': os,
            'asyncio': asyncio,
            'traceback': traceback,
            'sys': sys,
            'ast': ast,
        }

        exec(compile(parsed, filename="<ast>", mode="exec"), globals(), local_vars)
        result = await local_vars[fn_name](ctx, env)
        await ctx.send(result)
        await ctx.message.add_reaction("✅")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        await ctx.message.add_reaction("❌")

@bot.event
async def on_command_error(ctx: commands.Context, error):
  if isinstance(error, commands.CheckFailure):
    evalresponse = random.randint(0, len(responses))
    await ctx.send(f'<@{ctx.author.id}>')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

def run_bot():
    bot.run(token)

if __name__ == '__main__':
    run_bot()