import requests


class DiscordHelpers:
    @staticmethod
    async def create_thread(self, name, minutes, message):
        token = 'Bot ' + self._state.http.token
        url = f"https://discord.com/api/v9/channels/{self.id}/messages/{message.id}/threads"
        headers = {
            "authorization": token,
            "content-type": "application/json"
        }
        data = {
            "name": name,
            "type": 11,
            "auto_archive_duration": minutes
        }

        return requests.post(url, headers=headers, json=data).json()

    @staticmethod
    def get_channel(ctx, channel_id):
        for channel in ctx.guild.channels:
            if channel.id == channel_id:
                return channel
        return None

    @staticmethod
    async def get_message(channel, message_id, limit=200):
        for message in await channel.history(limit=limit).flatten():
            if message.id == message_id:
                return message

    @staticmethod
    def get_member(guild, member_or_id):
        member = guild.get_member_named(member_or_id)
        if member is None:
            try:
                member_id = int(member_or_id)
                member = guild.get_member(member_id)
                if member is None:
                    raise
            except:
                return None
        if member.bot:
            return None
        return member

    @staticmethod
    async def try_purge(channel, purge_size, silent=False):
        try:
            # Purge and delete the command
            await channel.purge(limit=purge_size + 1)
            # Send validation messages
            validation_message = f"Purged {purge_size} messages"
            print(validation_message)
            if not silent:
                await channel.send(validation_message)
        except:
            error_message = "Purge command not valid"
            print(error_message)
            if not silent:
                await channel.send(error_message)

    @staticmethod
    def is_private_message(message):
        return message.author.dm_channel is not None and message.author.dm_channel.id == message.channel.id

    # Roles
    admin_roles = ["Bureau", "Supremator"]
    @staticmethod
    def is_admin(author):
        try:
            if len(author.roles) == 0:
                return False
            role = author.roles[len(author.roles) - 1]
            return role.name in DiscordHelpers.admin_roles
        except:
            return False
    @staticmethod
    def get_roles(guild, role_names = []):
        roles = []
        for role in guild.roles:
            if role.name in role_names:
                roles.append(role)
        return roles
    @staticmethod
    def get_role(guild, role_name):
        for role in guild.roles:
            if role_name == role.name:
                return role
        return None
    @staticmethod
    def get_members_of_role(guild, role_names=[]):
        members_with_roles = []
        roles = DiscordHelpers.get_roles(guild, role_names)
        for member in guild.members:
            for role in roles:
                if role in member.roles:
                    members_with_roles.append(member)
                    break
        return members_with_roles

    # Channels
    @staticmethod
    def get_text_channel(guild, channel_id):
        for text_channel in guild.text_channels:
            if text_channel.id == channel_id:
                return text_channel
            
