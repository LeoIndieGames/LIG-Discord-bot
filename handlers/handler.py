from __future__ import annotations
import discord
import os
import json


class Handler:
    next_handler: Handler = None

    def __init__(self, file):
        file_path = os.path.dirname(file)
        config_file_path = os.path.join(file_path, "config.json")
        if os.path.isfile(config_file_path):
            with open(config_file_path, "r", encoding="utf-8") as config_file:
                self.data = json.loads(config_file.read())

        help_text_path = os.path.join(file_path, "help.txt")
        if os.path.isfile(help_text_path):
            with open(help_text_path, "r", encoding="utf-8") as help_file:
                self.help_text = help_file.read()
        else:
            self.help_text = ""

    def set_next_handler(self, handler: Handler) -> Handler:
        if self.next_handler is not None:
            return self.next_handler.set_next_handler(handler)
        else:
            self.next_handler = handler
            return self.next_handler

    def get_help_text(self) -> str:
        if self.next_handler:
            return self.help_text + "\n\n" + self.next_handler.get_help_text()
        else:
            return self.help_text

    async def handle_commands(self, message: discord.Message, args: str, admin: bool) -> bool:
        if len(args) > 0:
            if await self.__handle_commands__(message, args, admin):
                return True
            if self.next_handler:
                return await self.next_handler.handle_commands(message, args, admin)

    async def handle_message(self, message: discord.Message) -> bool:
        if await self.__handle_message__(message):
            return True
        if self.next_handler:
            return await self.next_handler.handle_message(message)

    async def handle_reaction(self, member: discord.Member, message: discord.Message, emoji: discord.PartialEmoji, added: bool):
        if await self.__handle_reaction__(member, message, emoji, added):
            return
        if self.next_handler:
            await self.next_handler.handle_reaction(member, message, emoji, added)

    async def handle_vc_update(self, member: discord.Member, before: discord.VoiceChannel, after: discord.VoiceChannel):
        await self.__handle_vc_update__(member, before, after)
        if self.next_handler:
            await self.next_handler.handle_vc_update(member, before, after)

    async def handle_start(self, bot: discord.Client):
        await self.__handle_start__(bot)
        if self.next_handler:
            await self.next_handler.handle_start(bot)

    async def handle_logout(self, bot: discord.Client):
        try:
            await self.__handle_logout__(bot)
        except:
            print(f"Something went wrong during __handle_logout__ of {__file__}")
        finally:
            if self.next_handler:
                await self.next_handler.handle_logout(bot)

    # Handle arguments of a command
    # Returns true if the message has been successfully handled
    # and the message's content shouldn't be handled
    # by self and/or next_handler
    async def __handle_commands__(self, message: discord.Message, args:str, admin: bool) -> bool:
        return False

    # Handle message content
    # Returns true if the message has been successfully handled
    # and shouldn't be handled by next_handler
    async def __handle_message__(self, message: discord.Message) -> bool:
        return False

    # Handle reaction event
    # Returns true if the reaction has been successfully handled
    # and shouldn't be handled by next_handler
    async def __handle_reaction__(self, member: discord.Member, message: discord.Message, emoji: discord.PartialEmoji, added: bool) -> bool:
        return False

    # Handle vc update
    async def __handle_vc_update__(self, member: discord.Member, before: discord.VoiceChannel, after: discord.VoiceChannel):
        pass

    # Handle start event
    async def __handle_start__(self, bot: discord.Client):
        pass

    # Handle logout event
    async def __handle_logout__(self, bot: discord.Client):
        pass