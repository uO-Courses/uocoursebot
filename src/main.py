
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


pat = re.compile(r"(.{3})(\d{4})")

def get_course(session: str, subject: str, course_code: int, year: int=year):
    resp = requests.get(
        f"https://uschedule.me/api/scheduler/v1/courses/query/?school=uottawa&course_code={course_code}&subject_code={subject.upper()}&season={session.lower()}&year={year}",
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
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.content.lower().startswith("uo!find"):
            msgtx = message.content.replace("uo!find ", "").lower()
            ans, b = parse_command(msgtx)
            spmsg = ""
            ff = "Fall"
            if ans == None and b:
                ff = "Winter"
                ans, _ = parse_command(f'winter {msgtx}')
            else:
                if "winter" in msgtx:
                    ans, _ = parse_command(f'{msgtx.replace("winter", "fall")}')
                    spmsg = "Course not found for Winter term but found for Fall term."
                else:
                    ans, _ = parse_command(f'{msgtx.replace("fall", "winter")}')
                    spmsg = "Course not found for Fall term but found for Winter term."
            if ans != None:
                if b:
                    await message.channel.send(f"No term specified, defaulting to {ff} {year}.")

                if spmsg != "":
                    await message.channel.send(spmsg)

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
                await message.channel.send(embed=emb)
            else:
                await message.channel.send(f"Could not find specified course ({msgtx.replace('winter ', '').replace('fall ', '').upper()})")


intents = discord.Intents.default()
intents.message_content = True
client = Uocourse(intents=intents)
client.run(os.environ.get("UOCBOT"))