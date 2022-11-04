from handlers.handler import Handler
import discord


class StreamRoleHandler(Handler):
    stream_message: discord.Message = None

    def __init__(self):
        super().__init__(__file__)

    async def __handle_commands__(self, message: discord.Message, args:str, admin: bool) -> bool:
        if args[0] == "stream" and admin:
            if len(args) > 1:
                if args[1] == "delete":
                    await self.delete_stream_message()
            else:
                await self.send_stream_message(message.channel)
            return True
        return False

    async def __handle_reaction__(self, member: discord.Member, message: discord.Message, emoji: discord.PartialEmoji, added: bool) -> bool:
        if not self.stream_message:
            return False
        if message.id != self.stream_message.id:
            return False

        if emoji == self.data["required_emoji_reaction"]:
            await self.add_stream_role_to_member(member)
        else:
            await message.remove_reaction(emoji, member)
        return True

    async def delete_stream_message(self):
        if self.stream_message:
            await self.stream_message.delete()
            self.stream_message = None

    async def send_stream_message(self, channel: discord.TextChannel):
        self.stream_message = await channel.send(self.data["message_text"])

    async def add_stream_role_to_member(self, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name=self.data["stream_role"])
        await member.add_roles(role)