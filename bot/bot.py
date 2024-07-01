import discord
import ast
import requests
import subprocess
import psutil
import os
import asyncio
import traceback
import sys
import random

from discord.ext import commands

import app.api.v2.players as v2
import app.settings

token = app.settings.DISCORD_BOT_TOKEN
intents = discord.Intents.default()
intents.message_content = True

guilds = [1244035145519075348, 1118543441538846811]

bot = commands.Bot(command_prefix="~", intents=intents, guilds=guilds)

allowed_user_ids = [360808288578830336]

def allowed(ctx):
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

responses = ["1", "2", "3", "4", "5"]

@bot.command()
@commands.check(allowed)
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
        if not result:
            await ctx.send("what am I supposed to respond...")
        else:
            await ctx.send(result)
        await ctx.message.add_reaction("✅")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        await ctx.message.add_reaction("❌")

@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user:
        return
    if before.content.startswith(bot.command_prefix) and before.content != after.content:
        await bot.process_commands(after)


@bot.slash_command(name="pf", description="user profile")
async def hello(
    ctx: discord.ApplicationContext,
    id: discord.Option(int)
):
    profile = await v2.get_player(id)
    ctx.respond(f'{profile}')


@bot.event
async def on_command_error(ctx: commands.Context, error):
  if isinstance(error, commands.CheckFailure):
    evalresponse = random.randint(0, len(responses))
    await ctx.send(f'<@{ctx.author.id}>')

def run_bot():
    bot.run(token)