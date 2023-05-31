import discord 
from discord.ui import Select, View

from lib.utils import embed_gen
from lib.rmp import get_prof
from lib.course import Courses

def register_prof(tree, client, uid_to_courses, gu):
    
    @tree.command(name="prof", description="View your courses")
    @discord.app_commands.choices(term=[
        discord.app_commands.Choice(name='Fall', value='Fall'),
        discord.app_commands.Choice(name='Winter', value='Winter')
    ])
    async def slash_03(intr01: discord.Interaction, course_code: str, term: discord.app_commands.Choice[str]="Fall"):
        cs = Courses()

        await intr01.response.defer()

        course, spmsg, worked, _, _ = cs(course_code, term)

        if worked:
            if spmsg != "":
                await intr01.channel.send(spmsg)

            profs = course.get_profs()

            if len(profs) != 0:

                sel = Select(placeholder="Select the professor",
                            options=[
                                discord.SelectOption(
                                    label=prof
                                ) for prof in profs
                            ])
                
                
                async def sel_callback(intr02: discord.Interaction):

                    selected_prof = sel.values[0]

                    emb = embed_gen(title=f"{selected_prof}", color = 10181046)

                    emb.add_field(name="Rating", value=f"{get_prof(profs[0])}/5")

                    await intr02.response.send_message(embed=emb)

                sel.callback = sel_callback

                view = View()
                view.add_item(sel)

                await intr01.followup.send(view=view)
            
            else:
                await intr01.followup.send("Unfortunately, no professors are known for this course.")

        else:
            await intr01.followup.send(spmsg)