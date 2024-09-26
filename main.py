import nextcord
from nextcord.ext import commands
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv
import asyncio
import random
import threading
import configparser

class Bot:
    config = configparser.ConfigParser()
    config.read('config.ini')

    intents = nextcord.Intents.default()
    intents.message_content = True
    client = commands.Bot(intents=intents)

    Name = config["BOT"]["BotName"]
    Token = config["BOT"]["BotToken"]
    serverID = config["BOT"]["ServerID"]
    JokeAPI = config["JOKES"]["JokeAPI"]


    CoinFlipList = ["Heads.", "Tails."]

    # Alert When bot is on.
    @client.event
    async def on_ready():
      print(f"{Bot.Name}  is  ready.")
    
    # Ping Command
    @client.slash_command(name="ping", description=f"Check {Name} latency.")
    async def Ping(interaction:nextcord.Interaction):
      latency = round(Bot.client.latency * 1000)
      await interaction.response.send_message(f'{Bot.Name} is online! Latency is {latency}ms.')

    # Coin flip
    @client.slash_command(name='flip', description="Flip a virtual coin.")
    async def coin(interaction: nextcord.Interaction):
      CoinChoice = random.choice(Bot.CoinFlipList)
      await interaction.response.send_message(CoinChoice)  

    @client.slash_command(name="list_commands", description="Lists all available commands")
    async def list_commands(interaction: nextcord.Interaction):
      await interaction.response.send_message(
          f"# List of commands\n"
          f" * `/gemini` - AI Assistant.\n"
          f" * `/kick` - Kicks a member from server.\n"
          f" * `/ping` - Checks the bot status.\n"
          f" * `/listcommands` - Lists all commands.\n"
          f" * `/flip` - Flips a virtual coin.\n"
    )  
   
    @client.slash_command(name="joke", description="Random Joke")
    async def joke(interaction: nextcord.Interaction):
      ReturnedJoke = APIcalls.GetJoke()
      print(ReturnedJoke)


    # Gemini
    @client.slash_command(name="gemini", description="Ask Gemini anything")
    async def gemini(interaction: nextcord.Interaction, message: str):  
      loop = asyncio.get_event_loop()
      response = await loop.run_in_executor(None, APIcalls.MessageGemini, message)
      await interaction.response.send_message(response)
   
    # Kick
    @client.slash_command(name="kick", description="Kicks a member from the server")
    @commands.has_permissions(kick_members=True) 
    async def kick(interaction: nextcord.Interaction, member: nextcord.Member, reason: str = None):
       try:
         await member.kick(reason=reason)
         await interaction.response.send_message(f"{member.mention} **has been kicked from the server. ✅**")
    
       except nextcord.Forbidden:
         await interaction.response.send_message("❌ **I don't have permission to kick this user.**")
    
       except nextcord.HTTPException as e:
         await interaction.response.send_message(f"❌ **An error occurred while trying to kick** {member.mention}: `{e}`")

class APIcalls:
  # Create gemini Model
  genai.configure(api_key=Bot.config["GEMINI"]["GeminiAPI"])

  generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
  }

  model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction=Bot.config["GEMINI"]["SystemInstruction"],
)

  chat_session = model.start_chat(history=[])

  def MessageGemini(input_message):
    response = APIcalls.chat_session.send_message(input_message)
    return response.text
  
  # Dad Joke
  
  def GetJoke():
     api_url = 'https://api.api-ninjas.com/v1/dadjokes?'

     try: 
       req = requests.get(api_url, headers={'X-Api-Key': Bot.JokeAPI})
       joke_data = req.json()
       joke = joke_data[0]['joke']
       print(joke_data)
      
     except Exception as e:
       return e


#BotThread = threading.Thread(target=Bot.client.run, args=Bot.Token).start()

# Debug (Remove before production)

def ReadConfig():
  print("Gemini API =" + Bot.config["GEMINI"]["GeminiAPI"])
  print("BotName =" + Bot.config["BOT"]["BotName"])
  print("Bot Token =" + Bot.config["BOT"]["BotToken"])
  print("Server ID =" + Bot.config["BOT"]["ServerID"])
  print("Joke API =" + Bot.config["JOKES"]["JokeAPI"])
  print("Joke Output = " + Bot.joke())

def GetJoke():
  APIcalls.GetJoke()