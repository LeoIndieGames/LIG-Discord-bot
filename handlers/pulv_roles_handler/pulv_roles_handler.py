from discord_helpers import DiscordHelpers
from handlers.handler import Handler
import discord


class CustomRole:
    def __init__(self, name: str, emoji: str, colors=None):
        if colors is None:
            colors = [150, 150, 150]
        self.name = name
        self.emoji = emoji
        self.color = discord.Colour.from_rgb(colors[0], colors[1], colors[2])

    def __str__(self):
        return f"{self.name}: {self.emoji}, {self.color}"


class PulvRolesHandler(Handler):
    def __init__(self):
        super().__init__(__file__)
        self.channel = None
        self.message = None

        # Populate custom roles
        self.custom_roles = []
        for role_str in self.data["roles"]:
            if len(role_str) > 2:
                custom_role = CustomRole(role_str[0], role_str[1], role_str[2])
            else:
                custom_role = CustomRole(role_str[0], role_str[1])
            self.custom_roles.append(custom_role)

    async def __handle_start__(self, bot: discord.Client):
        # Get role channel
        self.channel = bot.get_channel(self.data["channel_id"])

        # Get role message
        if self.channel:
            for message in await self.channel.history(limit=100).flatten():
                if message.author.bot and message.author.name == bot.user.name:
                    self.message = message
                    break
            if not self.message:
                await self.send_role_message()

        # Create role in guild if needed
        await self.create_roles_in_guild(bot.guilds[0])

        # Update roles
        for reaction in self.message.reactions:
            discord_role = self.get_discord_role_from_emoji(bot.guilds[0], reaction.emoji)

            # Get reaction authors and keep the members
            reaction_authors = await reaction.users().flatten()
            for abc in reaction_authors:
                if type(abc) == discord.user.User:
                    print(abc.display_name)
                    print(abc.id)
                    try:
                        await self.message.remove_reaction(reaction.emoji, abc)
                        reaction_authors.remove(abc)
                        print(self.data["reaction_removed_log"].replace("{username}", abc.display_name))
                    except:
                        pass

            # If no role has been found
            if not discord_role:
                await self.message.clear_reaction(reaction.emoji)
                continue

            all_members_of_role = DiscordHelpers.get_members_of_role(self.message.guild, role_names=[discord_role.name])

            # Remove role if needed
            for member in all_members_of_role:
                if member.bot:
                    continue
                if member not in reaction_authors:
                    await self.update_role_of_member(member, discord_role, False)

            # Add role if needed
            for author in reaction_authors:
                if type(author) == discord.user.User:
                    continue
                if author.bot:
                    continue
                if author not in all_members_of_role:
                    await self.update_role_of_member(author, discord_role, True)

    async def __handle_reaction__(self, member: discord.Member, message: discord.Message, emoji: discord.PartialEmoji, added: bool) -> bool:
        if message.id != self.message.id:
            return False
        if type(member) == discord.User:
            return False
        if member.bot:
            return False

        # Get custom role from emoji
        discord_role: discord.Role = self.get_discord_role_from_emoji(member.guild, emoji.name)
        if not discord_role:
            return True

        await self.update_role_of_member(member, discord_role, added)

    async def __handle_commands__(self, message: discord.Message, args:str, admin: bool) -> bool:
        if args[0] == "clear_pulv_roles" and admin:
            print("clear pulv roles")
            for custom_role in self.custom_roles:
                members = DiscordHelpers.get_members_of_role(message.guild, role_names=[custom_role.name])
                for member in members:
                    await member.remove_roles(DiscordHelpers.get_role(message.guild, custom_role.name))
            return True
        return False

    async def update_role_of_member(self, member: discord.Member, role: discord.Role, added: bool):
        # Add role if necessary
        if added and role not in member.roles:
            await member.add_roles(role)
            #await member.send(self.data["role_added_message"].replace("{role}", role.name))
            print(self.data["role_added_log"].replace("{role}", role.name).replace("{member}", member.display_name))

        # Remove role if necessary
        elif not added and role in member.roles:
            await member.remove_roles(role)
            #await member.send(self.data["role_removed_message"].replace("{role}", role.name))
            print(self.data["role_removed_log"].replace("{role}", role.name).replace("{member}", member.display_name))
        return True

    async def send_role_message(self):
        if not self.channel:
            return
        self.message = await self.channel.send(
            embed= discord.Embed(
                title=self.data["message_title"],
                description=self.data["message_description"]
            )
        )
        for custom_role in self.custom_roles:
            await self.message.add_reaction(custom_role.emoji)

    async def create_roles_in_guild(self, guild: discord.Guild):
        for custom_role in self.custom_roles:
            exist_in_guild = False

            for role in guild.roles:
                if role.name == custom_role.name:
                    exist_in_guild = True
                    break

            if not exist_in_guild:
                await guild.create_role(
                    name=custom_role.name,
                    colour=custom_role.color,
                    hoist=False,
                    mentionable=True
                )
                print(f"Created '{custom_role.name}' role")

    def get_discord_role_from_emoji(self, guild: discord.Guild, emoji) -> discord.Role:
        try:
            emoji = emoji.replace(" ", "")
        except:
            print(f"Error when parsing PartialEmoji: {emoji}")
            pass
        for custom_role in self.custom_roles:
            # print(f"{custom_role.emoji}\n{emoji.name}")
            if custom_role.emoji == emoji:
                discord_role = DiscordHelpers.get_role(guild, custom_role.name)
                if discord_role:
                    return discord_role
        return None
