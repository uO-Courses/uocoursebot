import discord, json
from discord.ui import Select, View

from lib.utils import parse_command, dayd, sttt, pat, year, embed_gen

def get_class(code, term): #/ -> (dict, msg, bool)
    fxcode = code.replace(' ', '').upper()
    ff = term.replace(' ', '').lower()
    msgtx = f"{ff} {fxcode}"
    ans, _ = parse_command(msgtx)
    spmsg = ""
    wrk = True

    if ans == None:
        if "winter" in msgtx:
            ans, _ = parse_command(f'{msgtx.replace("winter", "fall")}')
            spmsg = "Course not found for Winter term but found for Fall term."
        else:
            ans, _ = parse_command(f'{msgtx.replace("fall", "winter")}')
            spmsg = "Course not found for Fall term but found for Winter term."
    
    if ans == None:
        spmsg = f"Course not found ({fxcode})"
        wrk = False

    return ans, spmsg, wrk, msgtx, ff.upper()

def register_add(tree: discord.app_commands.CommandTree, client, uid_to_courses, gu):
    @tree.command(name="add", description="Add a course")
    async def slash_01(intr01: discord.Interaction, course_code: str, term: str="Fall"):
        userid = intr01.user.id

        await intr01.response.defer(thinking=True)
        ans, spmsg, worked, msgtx, ff = get_class(course_code, term)

        if worked:
            if spmsg != "":
                intr01.channel.send(spmsg)
            sls = []
            select = None
            if len(ans["sections"].keys()) < 25:
                select = Select(
                    placeholder="Choose your section",
                    options=[
                        discord.SelectOption(
                            label=f"Section {secc}",
                        ) for secc in ans["sections"].keys()
                    ]
                )

                sls.append(select)
            else:
                up = []
                sls = []
                i = 0
                n = 0
                for el in ans["sections"].keys():
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
            def get_just_some_callback(obj):
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
                        with open("utc.json", 'w') as f:
                            f.write(json.dumps(uid_to_courses, indent=4))
                return just_some_callback
            
            view = View()

            if select is not None:
                select.callback = get_just_some_callback(select)
            for el in sls:
                el.callback = get_just_some_callback(el)
                view.add_item(el)

            await intr01.followup.send(view=view, ephemeral=True)