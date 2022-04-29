﻿import discord
from discord.ext import commands
from discord.commands import permissions

class botnews_command(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="botnews")
    @permissions.has_any_role(951207540472029195, 951464246506565683)
    async def botnews(self, ctx):
        await ctx.message.delete()
        embed=discord.Embed(title="Update 1.10.1", description="What is new?", color=13565696)
        embed.set_author(name=f"{ctx.author.name}", url=f"https://discordapp.com/users/{ctx.author.id}", icon_url=f"{ctx.author.avatar.url}")
        embed.add_field(name="Commands", value="We have converted all commands to `/` commads.", inline=False)
        embed.add_field(name="Bug fixes", value="We fixed a few bugs, again. This probably has a few bugs due to the new features. So feel free to report any bugs to a Bot Developer, so they can work on fixing it soon.", inline=False)
        embed.set_footer(text="Stay tuned for the next update. 😉")
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(botnews_command(client))