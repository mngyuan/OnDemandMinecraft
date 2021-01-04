import discord
from discord.ext import commands
from configuration import Config
from server_management import manageServer
import boto3

bot = commands.Bot(command_prefix='>')
client = boto3.client(
    'ec2',
    aws_access_key_id=Config.ACCESS_KEY,
    aws_secret_access_key=Config.SECRET_KEY,
    region_name=Config.ec2_region
)

@bot.command()
async def start(ctx):
    message = manageServer(client, ctx)
    await ctx.send(message)

bot.run(Config.DISCORD_BOT_TOKEN)
