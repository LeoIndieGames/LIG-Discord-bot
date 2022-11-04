from discord_helpers import DiscordHelpers
from handlers.handler import Handler
import discord
import os
from pathlib import Path


class BotUtilities(Handler):
    def __init__(self, bot: discord.Client, bot_channel_id, original_handler: Handler, help_file_path: str) -> None:
        super().__init__(__file__)
        self.bot = bot
        self.bot_channel_id = bot_channel_id
        self.original_handler = original_handler if original_handler else self
        self.help_file_path = help_file_path

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> bool:
        if args[0] == "help" and admin:
            await message.author.send(content="Help message", file=discord.File(self.help_file_path))
            return True
        if args[0] == "logout" and admin:
            await self.original_handler.handle_logout(self.bot)
            await self.bot.close()
            return True
        if args[0] == "log_roles" and admin:
            if DiscordHelpers.is_private_message(message) or len(args) < 2:
                return True
            members_of_role = DiscordHelpers.get_members_of_role(message.guild, args[1:-1])
            text = f"Found {len(members_of_role)} accounts with at least one of the roles!\n"
            for member in members_of_role:
                text += member.name + ", "
            await message.channel.send(text)
        if args[0] == "separator":
            await message.channel.send(self.data["separator"] * self.data["separator_length"])
            await message.delete()
            return True
        if args[0] == "neutral_face":
            await message.channel.send(":neutral_face:")
            await message.delete()
            return True

        return False

    async def __handle_logout__(self):
        await self.bot.get_channel(self.bot_channel_id).send("Logging out!")
