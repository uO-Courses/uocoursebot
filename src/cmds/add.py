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
            if len(course.sections.keys()) < 25:
                select = Select(
                    placeholder="Choose your section",
                    options=[
                        discord.SelectOption(
                            label=f"Section {secc}",
                        ) for secc in course.sections.keys()
                    ]
                )

                sls.append(select)
            else:
                up = []
                sls = []
                i = 0
                n = 0
                for el in course.sections.keys():
                    if i >= 24:
                        sls.append(Select(
                            placeholder=f"Choose your section ({n})",
                            options=up
                        ))
                        up = []
                        i = 0
                        n += 1

                    up.append(discord.SelectOption(label=f"Section {el}"))

                    i+=1

                sls.append(Select(
                                placeholder=f"Choose your section ({n})",
                                options=up
                            ))

            ccode = "".join(pat.findall(msgtx)[0])

            
            view = View()

            if select is not None:
                select.callback = get_just_some_callback(select, ccode, uid_to_courses, userid, ff)
            for el in sls:
                el.callback = get_just_some_callback(el, ccode, uid_to_courses, userid, ff)
                view.add_item(el)

            await intr01.followup.send(view=view, ephemeral=True)
        else:
            intr01.followup.send(spmsg)