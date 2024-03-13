from discord.ext import commands


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_data = {}

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.server_data[guild.id] = {'IsRunning': False}
        print(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        del self.server_data[guild.id]

    @commands.command()
    async def id(self, ctx):
        await ctx.send(ctx.guild.id)


def setup(bot):
    bot.add_cog(Server(bot))
