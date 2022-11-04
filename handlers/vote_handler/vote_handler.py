from discord_helpers import DiscordHelpers
from handlers.vote_handler.vote import Vote
from handlers.handler import Handler
import discord
from discord_components import Button, ButtonStyle


class VoteHandler(Handler):
    def __init__(self):
        super().__init__(__file__)
        self.current_votes = []
        self.finished_votes = []

    async def __handle_start__(self, bot: discord.Client):
        self.bot = bot
        self.guild = bot.guilds[0]
        self.channel = bot.get_channel(self.data["channel_id"])

    async def __handle_commands__(self, message: discord.Message, args:str, admin: bool) -> bool:
        destroy_message = False
        if args[0] == "vote":
            if admin:
                # Create new vote
                if args[1] == "create":
                    title = " ".join(args[2:-1])
                    choices = args[-1].split(";")
                    await self.create_new_vote(self.bot, self.guild, title, choices)
                    destroy_message = True

                # Stop one or all votes
                elif args[1] == "stop":
                    if len(args) < 3:
                        return True
                    if args[2] == "all":
                        await self.stop_all_votes()
                    else:
                        await self.stop_vote(" ".join(args[2:]))
                    destroy_message = True

                # Reveal one vote result
                elif args[1] == "reveal":
                    if len(args) < 3:
                        return True
                    await self.channel.send(str(self.get_current_vote(" ".join(args[2:]))))
                    destroy_message = True

                # Reveal all results
                elif args[1] == "recap":
                    await self.show_recap()
                    destroy_message = True
            else:
                # Vote by command
                await self.get_current_vote(args[1]).add_vote(message.author, " ".join(args[2:]))
                destroy_message = True

            # Destroy message if needed
            if destroy_message and not DiscordHelpers.is_private_message(message):
                await message.delete()

            return True
        return False

    async def create_new_vote(self, bot: discord.Client, guild: discord.Guild, title: str, choices = []):
        # Create buttons
        components = []
        for i in range(0, len(choices)):
            components.append(Button(style=ButtonStyle.blue, label=choices[i], custom_id=choices[i]))

        message = await self.channel.send(self.data["temporary_vote_text"])
        embed = discord.Embed(
            title=f"**{title}**\t\t||id={message.id}||"
        )
        await message.edit(content="", embed=embed, components=components)

        new_vote: Vote = Vote(title, message, choices)
        self.current_votes.append(new_vote)

        while new_vote in self.current_votes:
            try:
                interaction = await bot.wait_for("button_click", check=lambda x: True)
                success = await new_vote.add_vote(interaction.user, interaction.custom_id)
                if success:
                    await interaction.send(content=self.data["vote_ephemeral_message"].replace("{choice}", interaction.custom_id))
                    print(self.data["vote_log"].replace("{title}", new_vote.name))
                else:
                    await self.channel.send(self.data["vote_fail_ephemeral_message"])
                print(new_vote)
            except:
                pass

    def get_current_vote(self, name_or_id) -> Vote:
        try:
            id = int(name_or_id)
            for vote in self.current_votes:
                if vote.id == id:
                    return vote
        except:
            name = name_or_id
            for vote in self.current_votes:
                if vote.name == name:
                    return vote
        return None

    async def stop_vote(self, name_or_id):
        vote: Vote = self.get_current_vote(name_or_id)
        self.finished_votes.append(vote)
        self.current_votes.remove(vote)
        text = self.data["vote_stopped_message"].replace("{vote_name}", vote.name)
        await self.channel.send(text)
        print(text)

    async def stop_all_votes(self):
        for i in range(0, len(self.current_votes)):
            self.finished_votes.append(self.current_votes[i])
        self.current_votes.clear()
        log = self.data["vote_all_stopped_message"]
        await self.channel.send(log)
        print(log)

    async def show_recap(self):
        recap = ""
        for i in range(0, len(self.finished_votes)):
            recap += str(self.finished_votes[i])
            if i != (len(self.finished_votes) - 1):
                recap += "\n"
        await self.channel.send(
            embed=discord.Embed(
                title="Vote recap: ",
                description=recap
            )
        )


