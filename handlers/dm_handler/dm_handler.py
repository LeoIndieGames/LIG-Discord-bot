from handlers.handler import Handler
from discord_helpers import DiscordHelpers
import discord
from handlers.dm_handler.dm_request import DmRequest


class DmHandler(Handler):
    def __init__(self) -> None:
        super().__init__(__file__)
        self.current_dm_requests = []

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> bool:
        if not admin:
            return False
        if DiscordHelpers.is_private_message(message):
            return False
        if args[0] == "dm":
            if len(args) < 3:
                return True
            receivers_str = args[1].split(";")
            await self.create_dm_request(message, receivers_str, " ".join(args[2:]))
            return True
        return False

    async def __handle_message__(self, message: discord.Message) -> bool:
        if len(self.current_dm_requests) == 0:
            return False
        for dm_request in self.current_dm_requests:
            if dm_request.author.id == message.author.id:
                message_content = message.content.lower()
                if "yes" in message_content:
                    await dm_request.send()
                    self.current_dm_requests.remove(dm_request)
                    await dm_request.channel.send(self.data["dm_sent_message"])
                    print(self.data["dm_sent_log"].replace("{author}", dm_request.author.display_name).replace("{receivers}", dm_request.receivers))
                elif "no" in message_content:
                    self.current_dm_requests.remove(dm_request)
                    await dm_request.channel.send(self.data["dm_cancelled_message"])

    async def create_dm_request(self, ctx: discord.Message, member_names, text):
        # Collect all receivers
        receivers = []
        for member_name in member_names:
            member = DiscordHelpers.get_member(ctx.guild, member_name)
            if member:
                if member not in receivers:
                    receivers.append(member)
            else:
                for member in DiscordHelpers.get_members_of_role(ctx.guild, member_name):
                    if member not in receivers:
                        receivers.append(member)

        # Cancel if no receivers
        if len(receivers) == 0:
            await ctx.send("No valid receivers found. Operation cancelled")
            return False

        self.current_dm_requests.append(DmRequest(ctx.author, receivers, text))

        # Concatenate receivers names
        receivers_names = ""
        for i in range(0, len(receivers)):
            receivers_names += receivers[i].name
            if i != (len(receivers) - 1):
                receivers_names += ", "

        # Ask user confirmation
        await ctx.send(self.data["dm_confirmation_message"].replace("{receivers}", receivers_names).replace("{text}", self.current_dm_requests[-1].text))
        return True
