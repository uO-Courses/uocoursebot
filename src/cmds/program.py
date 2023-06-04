import discord

from lib.sequence import get_engineering, eng, get_science, sci
from lib.sequence import program_maker

def register_program(tree: discord.app_commands.CommandTree, client: discord.Client, s_d, gu):
    
    g = discord.app_commands.Group(name="program", description="Find your program's course sequence.")

    program_maker(g, "science", sci, get_science, s_d)
    program_maker(g, "engineering", eng, get_engineering, s_d)

    tree.add_command(g)
