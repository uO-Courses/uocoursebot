import discord, json
from discord.ui import Select, View

from lib.utils import pat

from lib.course import Courses



def register_add(tree: discord.app_commands.CommandTree, client, s_d, gu):

    def get_just_some_callback(obj, ccode, uid_to_courses, userid, ff):
        async def just_some_callback(intr):

            if intr.user.id == userid:
                sl = obj.values[0]

                sec = sl.upper().replace("SECTION", "").replace(" ", "")
                tname = f"{ccode.upper()}-{sec}-{ff.upper()}"
                if tname in uid_to_courses:
                    if userid in uid_to_courses[tname]:
                        await intr.response.send_message("You have already added this section.")
                    else:
                        uid_to_courses[tname].append(userid)
                        r = []
                        for u in uid_to_courses[tname]:
                            ue = await client.fetch_user(u)
                            r.append(ue.name)

                        rr = '\n'.join(r)
                        await intr.response.send_message(f"Succesfully added {tname.upper()}. The following people are in this section: \n{rr}.", ephemeral=True)
                else:
                    uid_to_courses[tname] = [userid]
                    await intr.response.send_message(f"Succesfully added {tname.upper()}. You are the only person who has currently selected this section.", ephemeral=True)
                s_d.update_utc(uid_to_courses)
                s_d.set_preference(userid, 'has_added_courses', True)
        return just_some_callback

    @tree.command(name="add", description="Add a course")
    @discord.app_commands.choices(term=[
        discord.app_commands.Choice(name='Fall', value='Fall'),
        discord.app_commands.Choice(name='Winter', value='Winter')
    ])
    async def slash_01(intr01: discord.Interaction, course_code: str, term: discord.app_commands.Choice[str]="Fall"):

        uid_to_courses = s_d.utc

        term = term if type(term) is str else term.value

        userid = intr01.user.id
        cs = Courses()

        await intr01.response.defer(thinking=True)
        course, spmsg, worked, msgtx, ff = cs(course_code, term)

        if worked:
            if spmsg != "":
                intr01.channel.send(spmsg)
            sls = []
            select = None

            sls = [discord.SelectOption(label=f"Section {el}") for el in course.sections.keys()]
            fsls = [Select(placeholder=f"Choose your section ({int(x[1])+1})", options=x[0]) for x in [(sls[i:i+25], i/25) for i in range(0, len(sls), 25)]]

            ccode = "".join(pat.findall(msgtx)[0])

            view = View()

            for el in fsls:
                el.callback = get_just_some_callback(el, ccode, uid_to_courses, userid, ff)
                view.add_item(el)

            await intr01.followup.send(view=view, ephemeral=True)
        else:
            intr01.followup.send(spmsg)
