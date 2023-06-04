import discord

from lib.utils import dayd, sttt

from lib.embeds import Embedinator

from lib.course import Courses

def register_find(tree: discord.app_commands.CommandTree, client: discord.Client, uid_to_courses, gu):
    
    @tree.command(name="find", description="Find a course")
    @discord.app_commands.choices(term=[
        discord.app_commands.Choice(name='Fall', value='Fall'),
        discord.app_commands.Choice(name='Winter', value='Winter')
    ])
    async def slash_02(intr01: discord.Interaction, course_code: str, term: discord.app_commands.Choice[str]="Fall"):
        cs = Courses()

        term = term if type(term) is str else term.value

        await intr01.response.defer()

        course, spmsg, worked, _, _ = cs(course_code, term)

        if worked:
            if spmsg != "":
                intr01.channel.send(spmsg)
            
            ms = []

            for k, section in course.sections.items():
            
                tv = [f"Section {k}"] + [
                    f"{sttt[comp.status] if comp.status in sttt.keys() else '⚠️'} {kc} {dayd[comp.day]} {comp.start_time_12hr} - {comp.end_time_12hr}"
                    for kc, comp in section.components.items()
                ]
                profs = filter(lambda x: "Unknown" not in x, [comp.instructor for _, comp in section.components.items()])

                tv[0] += f" ({', '.join(list(set(profs)))})"
                    
                ms.append(tuple(tv))

            
            embd = Embedinator(intr01, ms)

            await embd.start()

        else:
            await intr01.followup.send(spmsg)