from discord_helpers import DiscordHelpers
import discord


class DmRequest:
    def __init__(self, author: discord.Member, channel: discord.TextChannel, receivers: list[discord.Member], text: str):
        self.author: discord.Member = author
        self.receivers: list[discord.Member] = receivers
        self.text: str = text
        self.channel = channel

    async def send(self):
        for receiver in self.receivers:
            if not receiver:
                continue
            await receiver.send(self.text)