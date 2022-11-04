from discord_helpers import DiscordHelpers 
from handlers.handler import Handler
import discord


class WorldCafeHandler(Handler):
    def __init__(self, bot: discord.Client) -> None:
        super().__init__(__file__)
        self.bot = bot

    async def __handle_start__(self, bot: discord.Client):
        self.world_cafe_channel = self.bot.get_channel(self.data["world_cafe_channel"])
        if not self.world_cafe_channel:
            print("World Cafe Channel not found")

    async def __handle_message__(self, message: discord.Message) -> bool:
        if DiscordHelpers.is_private_message(message):
            pass
        if message.channel.id == self.world_cafe_channel.id:
            success = False
            if message.reference:
                success = await self.send_answer(message.reference.message_id, message.content)
            else:
                success = await self.send_question(message.content)
            await message.delete()
            if not success:
                message.author.send(self.data["direct_message_error"])
            return True
        return False

    async def __handle_commands__(self, message: discord.Message, args: str, admin: bool) -> bool:
        args_length = len(args)
        
        # Ask a question in world cafe (>question blabalabalbalala balalaal)
        if args[0] == "question":
            # Not enough args
            if args_length < 2:
                return True
            question_message = await self.send_question(" ".join(args[1:]))
            if question_message:
                await message.author.send(f"{self.data['question_command_success']}{question_message.jump_url}")
            else:
                await message.author.send(self.data["question_command_fail"])
            return True

        # Remove all questions in world café (>clear_questions)
        if args[0] == "clear_questions" and admin:
            await message.author.send(self.data["clear_command_start"])
            if await self.clear_all_questions():
                text = self.data["clear_command_success"]
                print(text)
                await message.author.send(text)
            else:
                message.author.send(self.data["clear_command_fail"])
            return True

        # Get question id
        try:
            question_id = int(args[1])
        except:
            # Id is not an integer
            question_id = -1
            return False

        # Remove a question in world café (>remove_question message_id)
        if args[0] == "remove_question" and admin:
            # Not enough args
            if args_length < 2:
                return True
            if await self.remove_question(question_id):
                text = self.data["remove_command_success"].replace("{}", str(question_id))
            else:
                text = self.data["remove_command_fail"].replace("{}", str(question_id))
            print(text)
            await message.author.send(text)
            return True
            
        # Answer a question in world cafe (>answer message_id balablabal balbala)
        elif args[0] == "answer":
            # Not enough args
            if args_length < 3:
                return True
            if await self.send_answer(question_id, " ".join(args[2:])):
                text = self.data["answer_command_success"].replace("{}", str(question_id))
            else:
                text = self.data["answer_command_fail"].replace("{}", str(question_id))
            print(text)
            await message.author.send(text)
            return True

        return False

    async def __handle_reaction__(self, member: discord.Member, message: discord.Message, emoji: discord.PartialEmoji, added: bool):
        if added and message.channel.id == self.world_cafe_channel.id:
            await message.clear_reactions()
            await member.send(f"We don't judge in #{self.world_cafe_channel.name}")
            return True
        return False

    async def send_question(self, question: str) -> discord.Message:
        # Send the question
        question_message: discord.Message = await self.world_cafe_channel.send(f"{question}")
        print(f"id={question_message.id} // {question_message.content}")

        # Format the content of the question message
        await question_message.edit(content=f"{25*'-'}\n||id= *{question_message.id}*||\n{question_message.content}\n"
            + f"*To answer anonymously, reply to the question or send a private message to the bot with the following format '>answer {question_message.id} My answer...'*")

        return question_message

    async def get_question(self, question_id) -> discord.Message:
        return await self.world_cafe_channel.fetch_message(question_id)

    async def remove_question(self, question_id) -> bool:
        question_message = await self.get_question(question_id)
        if not question_message:
            return False
        await question_message.delete()
        return True

    async def clear_all_questions(self) -> bool:
        for message in await self.world_cafe_channel.history(limit=100).flatten():
            if message.author.bot:
                await message.delete()
        return True

    async def send_answer(self, question_id, answer) -> discord.Message:
        question_message = await self.get_question(question_id)
        if not question_message:
            return None
        
        new_message_content = question_message.content + f"\n\n- {answer}"
        await question_message.edit(content=new_message_content)
        return question_message