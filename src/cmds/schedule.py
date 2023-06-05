import discord

from lib.utils import dayd, sttt
from lib.permuter import ScheduleViewer

CURRENT_NUM = 0

def register_schedule(tree: discord.app_commands.CommandTree, client: discord.Client, s_d, gu):
    
    @tree.command(name="schedule", description="View your schedule")
    @discord.app_commands.choices(term=[
        discord.app_commands.Choice(name='Fall', value='Fall'),
        discord.app_commands.Choice(name='Winter', value='Winter')
    ])
    async def slash_02(intr01: discord.Interaction, term: discord.app_commands.Choice[str]="Fall"):
        term = term if type(term) is str else term.value

        await intr01.response.defer(thinking=True, ephemeral=True)

        sv = ScheduleViewer.from_user_id(s_d, 331431342438875137, term=term)

        await sv.start(intr01)