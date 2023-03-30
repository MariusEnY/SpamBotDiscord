from dotenv import load_dotenv
from discord.ext import commands
import discord
import random
import asyncio
import os

intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')


@client.command()
async def spam(ctx):
    num_messages = 200
    timeout_duration = 5  # in seconds

    # Get all the messages in the channel and randomly choose one
    messages = []
    async for message in ctx.channel.history(limit=num_messages):
        messages.append(message)
    random_message = random.choice(messages)

    # List with author + 3 random users
    users = ctx.channel.members
    users.remove(random_message.author)
    random_users = random.sample([user for user in users if not user.bot], k=3)
    random_users.append(random_message.author)
    random_users = random.sample(random_users, k=4)

    A_EMOJI = '\U0001F1E6'
    B_EMOJI = '\U0001F1E7'
    C_EMOJI = '\U0001F1E8'
    D_EMOJI = '\U0001F1E9'
    author_to_letter = {}
    emojis = [A_EMOJI, B_EMOJI, C_EMOJI, D_EMOJI]  # A, B, C, D
    for i, author in enumerate(random_users):
        author_to_letter[author] = emojis[i]

    # Add reactions to msg
    for author, letter in author_to_letter.items():
        reaction = letter
        await message.add_reaction(letter)

    # Create the question message
    mcq_message_text = f"**Guess the spammer:**\n\n{random_message.content}\n\n"
    for author in random_users:
        mcq_message_text += f"{author_to_letter[author]}) {author.name}\n"

    # Send the MCQ message
    mcq_message = await ctx.send(mcq_message_text)

    # Add reacts to msg
    for author in random_users:
        letter = author_to_letter[author]
        await mcq_message.add_reaction(letter)

    # Wait
    await asyncio.sleep(timeout_duration)

    # Get all the reactions
    reaction_message = await ctx.fetch_message(mcq_message.id)
    reactions = reaction_message.reactions

    # Create a set of the users who guessed the correct author
    correct_users = set()
    for reaction in reactions:
        if reaction.emoji in author_to_letter.values():
            async for user in reaction.users():
                if user != client.user:
                    if reaction.emoji == A_EMOJI:
                        author = random_users[0]
                    elif reaction.emoji == B_EMOJI:
                        author = random_users[1]
                    elif reaction.emoji == C_EMOJI:
                        author = random_users[2]
                    elif reaction.emoji == D_EMOJI:
                        author = random_users[3]
                    if random_message.author == author:
                        correct_users.add(user)

    # Check answers
    if len(correct_users) == 0:
        await message.channel.send("Nobody guessed the correct answer :(")
    else:
        correct_user_mentions = [user.mention for user in correct_users]
        correct_user_list = ", ".join(correct_user_mentions)
        await message.channel.send(f"The following users guessed correctly: {correct_user_list}")

    await message.channel.send(f"The correct answer was: {random_message.author.name}")

# Run the bot
load_dotenv()
token = os.environ['DISCORD_TOKEN']
print(token)
client.run(token=token)
