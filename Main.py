import discord
from discord.ext import commands
import random
from colorama import Fore, just_fix_windows_console
from datetime import datetime
import json
import requests
from os import system

system('cls')
system(f"title Tao Farmer v1")

# Load token from config.json
with open('token.json') as config_file:
    config = json.load(config_file)
    token = config['token']
    webhook_url = config['webhook_url']

bot = commands.Bot(command_prefix='?', description='description', self_bot=True)
just_fix_windows_console()

# Initialize a counter for successful button clicks
successful_clicks = 0

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    system(f"title Tao Farmer v1 [=] {bot.user.name}")  # Set window title when bot is ready


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages sent by the bot itself
    
    # Check if the message is from the "Human Validation Bot" and contains the specific prompt
    if message.author.name == "Human Validation Bot" and "Vote for the three best representations of the prompt below." in message.content:
        await handle_button_click_with_retry(message)

async def handle_button_click_with_retry(message):
    global successful_clicks  # Use global keyword to modify the counter
    max_retries = 3
    for _ in range(max_retries):
        try:
            await process_button_click(message)
            successful_clicks += 1  # Increment counter on successful click
            await send_webhook_message(message)  # Send webhook message on successful click
            break  # If successful, exit the loop
        except Exception as e:
            print(Fore.RED, f'[{datetime.now()}] Failed to handle button click: {e}')
            print(Fore.RED, f'[{datetime.now()}] Retrying...')
    else:
        print(Fore.RED, f'[{datetime.now()}] Failed to handle button click after {max_retries} attempts')

async def process_button_click(message):
    components = message.components
    if not components:
        print(f'No components found in {message.guild.name} > {message.channel.name}')
        print(f'Message Content: {message.content}')
        return

    print("Components in the message:")
    # Flatten the list of buttons
    buttons = [button for component in components for button in component.children if isinstance(button, discord.Button)]
    if not buttons:
        print(f'No buttons found in {message.guild.name} > {message.channel.name}')
        print(f'Message Content: {message.content}')
        return

    random_buttons = random.sample(buttons, min(len(buttons), 3))
    for button in random_buttons:
        result = await button.click()

    # Print outside the loop to avoid multiple prints for each button click
    print(Fore.GREEN, f'[{datetime.now()}] [+]Clicked {result} in {message.guild.name} > {message.channel.name}')
    print(Fore.GREEN, f'[{datetime.now()}] [~] Message Content: {message.content}')
    print(Fore.CYAN, f'[{successful_clicks}]')

    return result

async def send_webhook_message(message):
    embed = discord.Embed(
        title="Button Click Successful!",
        description=f"A button click was successful in {message.guild.name} > {message.channel.name}",
        color=discord.Color.green()
    )
    embed.add_field(name="Message Content", value=message.content)
    embed.add_field(name="Timestamp", value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    data = {
        "username": "top g",
        "avatar_url": "https://cdn.sanity.io/images/u4eaiudq/production/7a1362c5507179a48e203b66670ea4b505d9135a-1080x1080.png",  # Change to your desired avatar URL
        "embeds": [embed.to_dict()]
    }

    response = requests.post(webhook_url, json=data)
    if response.status_code != 200:
        print(Fore.GREEN, f' {response.text}')

bot.run(token)
