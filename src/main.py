
"""
    Copyright (C) 2023 Ann Mauduy-Decius

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import requests, json, os, re
import discord
from discord.ui import Select, View

# a course section ID should be like FRA1528-A
uid_to_courses = {
     
}

with open("utc.json", 'r') as f:
    uid_to_courses = json.loads(f.read())

# uid -> course code
AW_MSG_FRM = {
    
}

dayd = {
    "MO": "Monday",
    "TU": "Tuesday",
    "WE": "Wednesday",
    "TH": "Thursday",
    "FR": "Friday",
    "SA": "Saturday",
    "SU": "Sunday"
}

sttt = {
    "OPEN": "🟢",
    "CLOSED": "🔴"
}

year = 2023


pat = re.compile(r"(.{3})(\d{4}\d?)")

def get_course(session: str, subject: str, course_code: int, yr: int=year):
    if session.lower() == "winter":
        yr = 2024

    resp = requests.get(
        f"https://uschedule.me/api/scheduler/v1/courses/query/?school=uottawa&course_code={course_code}&subject_code={subject.upper()}&season={session.lower()}&year={yr}"
    )

    rj = resp.json()

    return rj["data"]

def parse_command(text: str):
    sess=None
    b=False
    if "fall" in text:
        sess="fall"
    if "winter" in text:
        sess="winter"

    if sess == None:
        # Unsupported session
        sess="fall"
        b = True

    ans = pat.findall(text)[0]

        
    return get_course(session=sess, subject=ans[0], course_code=ans[1]), b




class Uocourse(discord.Client):
    async def on_ready(self):
        await tree.sync(guild=discord.Object(1095372141966393364))
        print('Logged in as', self.user)

    async def on_message(self, message):
            
        pass

intents = discord.Intents.default()
intents.message_content = True
client = Uocourse(intents=intents)
tree = discord.app_commands.CommandTree(client)

@tree.command(name="me", description="View your courses", guild=discord.Object(1095372141966393364))
async def slash_03(intr01: discord.Interaction):
    userid = intr01.user.id
    rrr=""
    await intr01.response.defer(thinking=True)
    for k, v in uid_to_courses.items():
        if userid in v:
            r = []
            for u in v:
                ue = await client.fetch_user(u)
                r.append(ue.name)

            rr = ', '.join(r)
            rrr += (f"You have selected the section {k}. The following people are in this section: {rr}.\n")
        
    await intr01.followup.send(rrr)

@tree.command(name="find", description="Find a course", guild=discord.Object(1095372141966393364))
async def slash_02(intr01: discord.Interaction, course_code: str, term: str="Fall"):
    userid = intr01.user.id
    msgtx = f"{term.lower()} {course_code.replace(' ', '')}"
    ans, b = parse_command(msgtx)
    spmsg = ""
    ff = "Fall"

    await intr01.response.defer(thinking=True)
    if ans == None and b:
        ff = "Winter"
        ans, _ = parse_command(f'winter {msgtx}')
    if ans == None:
        if "winter" in msgtx:
            ans, _ = parse_command(f'{msgtx.replace("winter", "fall")}')
            spmsg = "Course not found for Winter term but found for Fall term."
        else:
            ans, _ = parse_command(f'{msgtx.replace("fall", "winter")}')
            spmsg = "Course not found for Fall term but found for Winter term."
    if ans != None:
        if b:
            await intr01.channel.send(f"No term specified, defaulting to {ff} {year}.")
            
        if spmsg != "":
            await intr01.channel.send(spmsg)

        emb = discord.Embed(title=f"{ ans['course_name'] } ({ans['subject_code']}{ans['course_code']})", color=33023)

        for k, section in ans["sections"].items():
            tt = f"Section {k}"
            tv = []
            profs = []
            for kc, comp in section["components"].items():
                prof = comp["instructor"]
                if prof not in profs:
                    profs.append(prof)
                if comp["status"] in sttt.keys():
                    st = sttt[comp["status"]]
                else: 
                    st = "⚠️"
                tv.append(
                    f"""
                        {st} {kc} {dayd[comp['day']]} {comp['start_time_12hr']} - {comp['end_time_12hr']}
                    """
                )
            emb.add_field(name=f"{tt} ({', '.join(profs)})", value="".join(tv), inline=False)
        await intr01.followup.send(embed=emb)
    else:
        await intr01.channel.send(f"Could not find specified course ({msgtx.replace('winter ', '').replace('fall ', '').upper()})")

@tree.command(name="remove", description="Remove a course", guild=discord.Object(1095372141966393364))
async def slash_04(intr01: discord.Interaction):
    userid = intr01.user.id
    await intr01.response.defer(thinking=True)
    emb = discord.Embed(title="Choose which section to remove.")

    ss = []
    for k, v in uid_to_courses.items():
        if userid in v:
            ss.append(k)

    emb.add_field(name="Currently selected courses", value="\n".join(ss))

    sel = Select(
        placeholder="Choose the section to remove",
        options=[
            discord.SelectOption(label=k) for k in ss
        ]
    )

    async def selection_callback(intr01: discord.Interaction):
        if intr01.user.id == userid:
            await intr01.response.defer()
            val = sel.values[0]
            
            v = uid_to_courses[val]
            if userid in v:
                v.remove(userid)
            with open("utc.json", 'w') as f:
                f.write(json.dumps(uid_to_courses, indent=4))

            await intr01.followup.send(f"Sucessfully deleted {val}.")
            

    sel.callback = selection_callback
    view = View()
    view.add_item(sel)
    
   

    await intr01.followup.send(embed=emb, view=view)

@tree.command(name="add", description="Add a course", guild=discord.Object(1095372141966393364))
async def slash_01(intr01: discord.Interaction, course_code: str, term: str="Fall"):
    userid = intr01.user.id
    msgtx = f"{term.lower()} {course_code.replace(' ', '')}"
    ans, b = parse_command(msgtx)
    spmsg = ""
    ff = term

    await intr01.response.defer(thinking=True)
    if ans == None and b:
        ff = "Winter"
        ans, _ = parse_command(f'winter {msgtx}')
    if ans == None:
        if "winter" in msgtx:
            ff = "fall"
            ans, _ = parse_command(f'{msgtx.replace("winter", "fall")}')
            spmsg = "Course not found for Winter term but found for Fall term."
        else:
            ff = "winter"
            ans, _ = parse_command(f'{msgtx.replace("fall", "winter")}')
            spmsg = "Course not found for Fall term but found for Winter term."
    if ans != None:
        if b:
            await intr01.channel.send(f"No term specified, defaulting to {ff} {year}.")

        if spmsg != "":
            await intr01.channel.send(spmsg)

        
        emb = discord.Embed(title="Please choose which section you are enrolled in.", color=33023)
        ornth = lambda x: ["Unknown"] if x == [] else x
        i = 0
        n = 1
        l = [f"Section {k} ({', '.join(ornth(list(set([c['instructor'] for (_, c) in v['components'].items()]))))})" for (k, v) in ans["sections"].items()]
        ss = ""
        for el in l:
            if i > 9:
                i = 0
                emb.add_field(name=f"Available sections ({n})", value=ss)
                n+=1
                ss = ""
            ss+=el+"\n"

            i+=1

        emb.add_field(name=f"Available sections ({n})", value=ss)
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
                            await intr.response.send_message(f"Succesfully added {tname.upper()}. The following people are in this section: \n{rr}.")
                    else:
                        uid_to_courses[tname] = [userid]
                        await intr.response.send_message(f"Succesfully added {tname.upper()}. You are the only person who has currently selected this section.")
                    with open("utc.json", 'w') as f:
                        f.write(json.dumps(uid_to_courses, indent=4))
            return just_some_callback
        
        view = View()

        if select is not None:
            select.callback = get_just_some_callback(select)
        for el in sls:
            el.callback = get_just_some_callback(el)
            view.add_item(el)

        await intr01.followup.send(embed=emb, view=view)

client.run(os.environ.get("UOCBOT"))
