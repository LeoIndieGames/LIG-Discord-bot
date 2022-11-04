import os
from handlers.handler import Handler
import discord
import random


class HumorHandler(Handler):
    def __init__(self) -> None:
        super().__init__(__file__)
        with open(os.path.join(os.path.dirname(__file__), "jokes.txt"), "r", encoding='utf8') as file:
            self.jokes = []
            for line in file.readlines():
                if line == "":
                    continue
                self.jokes.append(line)

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> bool:
        if args[0] == "joke":   
            await message.delete()
            await self.trigger_joke(message.channel)
            return True
        if args[0] == "xd":
            await message.channel.send("XDDDDDDD")
            await message.delete()
            return True
        return False

    async def __handle_message__(self, message: discord.Message) -> bool:
        if message.author.bot or message.channel.id not in self.data["white_list_channels"]:
            return False

        content = message.content.lower()
        for word in self.data["joke_trigger_words"]:
            if word in content:
                test = random.randint(0, self.data["joke_proba"]-1) 
                if test == 0:
                    await self.trigger_joke(message.channel)
                    return True
        return False

    async def trigger_joke(self, channel: discord.TextChannel):
        await channel.send(self.jokes[random.randint(0, len(self.jokes)-1)])
        if random.randint(0, self.data["answer_proba"]-1) == 0:
            answers = self.data["answers"]
            await channel.send(answers[random.randint(0, len(answers)-1)])
    