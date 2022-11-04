import json
from handlers.handler import Handler
import random
import discord
import os


class CatPatroller(Handler):
    def __init__(self):
        super().__init__(__file__)
        self.cat_patrol: bool = True
        self.cat_channel_id = self.data["cat_channel_id"]

        # Collect color from json
        color_tuple = tuple(self.data["mp_warning_color"])
        self.mp_warning_color = discord.Colour.from_rgb(color_tuple[0], color_tuple[1], color_tuple[2])

        # Populate allowed cats
        self.ALLOWED_CATS = []
        with open(os.path.join(os.path.dirname(__file__), "cat-gifs.txt"), "r") as file:
            for line in file.readlines():
                if line == "":
                    continue
                line = line.removesuffix("\n")
                self.ALLOWED_CATS.append(line)

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> bool:
        args_len: int = len(args)
        if args[0] == "cat_patrol" and admin:
            if args_len > 1:
                self.cat_patrol = "on" in args[1].lower()
            await message.channel.send(f"Cat patrol is {'on' if self.cat_patrol else 'off'}.")
            return True
        elif args[0] == "cat":
            await message.channel.send(self.ALLOWED_CATS[random.randint(0, len(self.ALLOWED_CATS)-1)])
            await message.delete()
            return True
        return False

    async def __handle_message__(self, message: discord.Message) -> bool:
        if not self.cat_patrol:
            return False

        # Remove not allowed cats in cat channel
        if message.channel.id == self.cat_channel_id:
            if message.content not in self.ALLOWED_CATS or len(message.attachments) > 0:
                # Remove message
                await message.delete()
                print(f"Removed message '{message.content}' from '{message.author.display_name}' in the channel #{message.channel.name}")

                # Send private message to author
                text = discord.Embed(
                    title=self.data["mp_warning_title"],
                    description=self.data["mp_warning_description"],
                    colour= self.mp_warning_color
                )
                await message.author.send(embed=text)
                await message.author.send(self.data["mp_warning_gif"])
                print(f"Sent cat patrol warning message to '{message.author.display_name}'")
                return False