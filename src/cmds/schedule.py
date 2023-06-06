import discord

from discord.ui import Select

from lib.utils import dayd, sttt
from lib.permuter import ScheduleViewer
from lib.data import SharedData

CURRENT_NUM = 0

def get_callbacker(item: Select, id, sv: ScheduleViewer, s_d: SharedData, userid, term):

    async def callback(intr01: discord.Interaction):

        if intr01.user.id == userid:


            res = int(item.values[0])

            if res != -1 and not sv.check_if_fits(sv.options[id][res]):
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

                    pref = s_d.get_preference(intr01.user.id, '_n_course_selection')

                    pref[term] = sv.selected

                    s_d.set_preference(intr01.user.id, '_n_course_selection', pref)
                    
                    await intr01.followup.send(embed=emb, file=file)
                else:
                    await intr01.response.defer(thinking=True, ephemeral=True)

                    txt = "Succesfully selected no component."
                    if res != -1:
                        c = sv.options[id][sv.selected[id]]
                        txt = f"Succesfully selected component {c[0]}."
                    await intr01.followup.send(txt)

    return callback


def register_schedule(tree: discord.app_commands.CommandTree, client: discord.Client, s_d: SharedData, gu):
    
    @tree.command(name="schedule", description="View your schedule")
    @discord.app_commands.choices(term=[
        discord.app_commands.Choice(name='Fall', value='Fall'),
        discord.app_commands.Choice(name='Winter', value='Winter')
    ])
    @discord.app_commands.describe(
        reset="Whether to reselect the course components",
        term="Which term's schedule to view"
    )
    async def slash_02(intr01: discord.Interaction, term: discord.app_commands.Choice[str]="Fall", reset: bool=False):

        await intr01.response.defer(thinking=True, ephemeral=False)

        term = term if type(term) is str else term.value

        pref = s_d.get_preference(intr01.user.id, '_n_course_selection')


        if reset:

            pref[term] = []

            s_d.set_preference(intr01.user.id, '_n_course_selection', pref)


        sv = ScheduleViewer.from_user_id(s_d, intr01.user.id, term=term)

        if len(pref[term]) == len(sv.selected):


            sv.selected = pref[term]

            sv.generate()

            emb, file = sv.get_embed()
            
            await intr01.followup.send(embed=emb, file=file)


        else:

            sls = [
                (j, Select(
                    placeholder=f"Choose your {x[0][6]} for {x[0][7]}",
                    options=[discord.SelectOption(label=f"{y[0]} ({y[8].rday} {y[8].start_time_12hr} - {y[8].end_time_12hr})", value=i) for i, y in enumerate(x)] + [discord.SelectOption(label="None", value = -1)]
                ))
                for j, x in enumerate(sv.options)
            ]

            view = discord.ui.View()

            if len(sls) > 5:
                views = []
                for x in [sls[i:i+5] for i in range(0, len(sls), 5)]:
                    view = discord.ui.View()
                    for y in x:
                        y[1].callback = get_callbacker(y[1], y[0], sv, s_d, intr01.user.id, term)
                        view.add_item(y[1])
                    views.append(view)

                for view in views:
                    await intr01.followup.send("Please select each component to generate your schedule.", view=view)
            else:
                for a, s in sls:
                    s.callback = get_callbacker(s, a, sv, s_d, intr01.user.id, term)
                    view.add_item(s)

                await intr01.followup.send("Please select each component to generate your schedule.", view=view)