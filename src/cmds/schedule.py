import discord

from discord.ui import Select

from lib.utils import dayd, sttt
from lib.permuter import ScheduleViewer

CURRENT_NUM = 0

def get_callbacker(item: Select, id, sv: ScheduleViewer):

    async def callback(intr01: discord.Interaction):


        res = item.values[0]

        if not sv.check_if_fits(sv.options[id][res]):
            await intr01.response.defer(thinking=True, ephemeral=True)

            txt = f"This component conflicts with your other selected components (\n{sv.why})."
            await intr01.followup.send(txt)

            res = -1
            sv.max[id] = False

        else:
            sv.selected[id] = int(res)
            sv.max[id] = True

            if all(sv.max.values()):
                await intr01.response.defer(thinking=True, ephemeral=False)

                sv.generate()

                emb, file = sv.get_embed()
                
                await intr01.followup.send(embed=emb, file=file)
            else:
                await intr01.response.defer(thinking=True, ephemeral=True)

                txt = "Succesfully selected no component."
                if res != -1:
                    c = sv.options[id][sv.selected[id]]
                    txt = f"Succesfully selected component {c[0]}."
                await intr01.followup.send(txt)

    return callback


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

        sls = [
            (j, Select(
                placeholder=f"Choose your {x[0][6]} for {x[0][7]}",
                options=[discord.SelectOption(label=f"{y[0]} ({y[8].rday} {y[8].start_time_12hr} - {y[8].end_time_12hr})", value=i) for i, y in enumerate(x)] + [discord.SelectOption(label="None", value = -1)]
            ))
            for j, x in enumerate(sv.options)
        ]

        view = discord.ui.View()

        for a, s in sls:
            s.callback = get_callbacker(s, a, sv)
            view.add_item(s)

        await intr01.followup.send("Please select each component to generate your schedule.", view=view)