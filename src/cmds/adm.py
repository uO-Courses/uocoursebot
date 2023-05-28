import discord, time

from lib.utils import embed_gen, pretty_print_user, get_time

etime = time.time()

def register_adm(tree, client, uid_to_courses, gu):
    
    @tree.command(name="runtime", description="View how long the bot has been running")
    async def slash_03(intr01: discord.Interaction):
        await intr01.response.send_message(f"The bot has been running for {get_time(int(time.time() - etime))}.")