import asyncio
from discord.ext import commands


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start(self, ctx, nplayers):
        server_id = ctx.guild.id
        IsRunning = self.bot.get_cog('Server').server_data.get(
            server_id, {}).get('IsRunning', False)

        if IsRunning:
            await ctx.send("already running lil bro")
            return
        nplayers = int(nplayers)
        if nplayers > 9:
            await ctx.send(f'number of players {nplayers}, is too large, the max number of players is 9')
            return
        elif nplayers < 2:
            await ctx.send("not enough players")
            return
        elif nplayers == 2:
            await ctx.send(f"Game started but the recommended number of players is greater than {nplayers}")
            IsRunning = True
        else:
            await ctx.send(f'Game started with {nplayers} players, {ctx.author.mention} type ">play" to join.')
        self.bot.get_cog('Server').server_data[server_id]['IsRunning'] = True

        def check(msg, mentioned=None):
            if msg.author == ctx.author and msg.content.lower() == '>play':
                self.bot.get_cog(
                    'Server').server_data[server_id]['IsRunning'] = True

        try:
            await self.bot.wait_for('message', timeout=60, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Timeout. Not enough players.')
        else:
            await ctx.send(f'{ctx.author.mention} joined the game!')

    @commands.command()
    async def userping(self, ctx, arg):
        await ctx.send("dwiajo")


def setup(bot):
    bot.add_cog(Game(bot))
