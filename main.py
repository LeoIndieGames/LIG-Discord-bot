import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Discord modules imports
import discord
from discord_components import DiscordComponents
from discord.ext import commands

# Import all handler and helpers class
from handlers_imports import *
from discord_helpers import DiscordHelpers

# Get parameters from config.json
config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
help_file_path = os.path.join(os.path.dirname(__file__), "help.txt")
with open(config_file_path, "r", encoding="utf-8") as config_file:
    config = json.loads(config_file.read())
COMMAND_PREFIX = config["command_prefix"]
bot_channel_id = config["bot_channel_id"]

# Intents
intents = discord.Intents.all()
intents.members = True

# Create bot
bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
    description=config["bot_description"]
)
DiscordComponents(bot)
bot.remove_command("help")

# Set up handlers chain of command
handler: Handler = BotUtilities(bot, bot_channel_id, None, help_file_path)
handler.set_next_handler(HumorHandler()).set_next_handler(CatPatroller()).set_next_handler(DmHandler()) \
    .set_next_handler(TrollsHandler()).set_next_handler(PurgeHandler()).set_next_handler(WorldCafeHandler(bot)) \
    .set_next_handler(StreamRoleHandler()).set_next_handler(PulvRolesHandler()).set_next_handler(VoteHandler()) \
    .set_next_handler(DmHandler())


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=config["playing_activity"]))
    print('------' * 5)
    print(f"Logged in as {bot.user.name}")
    print(f"Bot user id: {bot.user.id}")
    print(f"Initializing...")
    await handler.handle_start(bot)
    with open(help_file_path, "w", encoding="utf-8") as help_file:
        help_file.write(handler.get_help_text())
    print(f"\n{bot.user.name} is ready!")
    print('------' * 5)


@bot.event
async def logout_bot():
    try:
        await handler.handle_logout(bot)
    except:
        pass
    finally:
        print(f"{bot.user.name} disconnecting...")
        msg = "**Now offline " + str(datetime.now()) + "** \n / / / / / / / / "
        await bot.get_channel(bot_channel_id).send(msg)
        await bot.close()


@bot.event
async def on_message(message):
    if not message.author.bot and len(message.content) > 0:
        message_content: str = message.content.lower()

        # Handle handlers command
        successful_command = False
        if message_content.startswith(COMMAND_PREFIX):
            args = message_content
            while args.startswith(COMMAND_PREFIX):
                args = args.removeprefix(COMMAND_PREFIX)
            args = args.split()
            successful_command = await handler.handle_commands(message, args, DiscordHelpers.is_admin(message.author))
            print(f"Try handle command: success={successful_command}")

        # Handle message
        if not successful_command:
            print(f"Try handle message")
            await handler.handle_message(message)


@bot.event
async def on_voice_state_update(member, before, after):
    await handler.handle_vc_update(member, before, after)


@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    channel = bot.get_channel(payload.channel_id)
    message = await DiscordHelpers.get_message(channel, payload.message_id)
    author = guild.get_member(payload.user_id)
    if not author:
        return
    if author.bot:
        return

    print("Try Handle reaction added")
    await handler.handle_reaction(author, message, payload.emoji, added=True)


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    channel = bot.get_channel(payload.channel_id)
    message = await DiscordHelpers.get_message(channel, payload.message_id)
    author = guild.get_member(payload.user_id)
    if not author:
        return
    if author.bot:
        return

    print("Try handle reaction removed")
    await handler.handle_reaction(author, message, payload.emoji, added=False)

# Launch bot
if __name__ == '__main__':
    load_dotenv()
    bot.run(os.getenv("TOKEN"))
