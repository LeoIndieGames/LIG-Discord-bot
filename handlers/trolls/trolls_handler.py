from discord_helpers import DiscordHelpers
from handlers.handler import Handler
import discord


class TrollsHandler(Handler):
    def __init__(self) -> None:
        super().__init__(__file__)

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> bool:
        args_length = len(args)
        if args[0] == "rickastley":
            await message.channel.send(f"{message.author.display_name.split()[0]} summoned Rick Astley!\n{self.data['rickastley_gif']}")
            await message.delete()
            return True
        if args[0] == "rickroll":
            if args_length > 1:
                member: discord.Member = DiscordHelpers.get_member(message.guild, args[1])
                if member:
                    await member.send(f"Get rickrolled by {message.author.display_name.split()[0]}\n{self.data['rickastley_gif']}")
                    await message.delete()
            return True

        if args[0] == "google":
            if args_length > 2:
                member: discord.Member = DiscordHelpers.get_member(message.guild, args[1])
                if member:
                    url = self.data["googler_url"] + "+".join(args[2:])
                    await message.channel.send(f"{member.mention}, {message.author.display_name.split()[0]} told me to give you this:\n{url}")
                    await message.delete()
            return True
            
        return False