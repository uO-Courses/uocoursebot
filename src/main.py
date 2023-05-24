
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

import requests, json, os

import discord

from enum import Enum

import re

import discord


pat = re.compile(r"(.{3})(\d{4})")

def get_course(session: str, subject: str, course_code: int, year: int=2023):
    resp = requests.get(
        f"https://uschedule.me/api/scheduler/v1/courses/query/?school=uottawa&course_code={course_code}&subject_code={subject.upper()}&season={session.lower()}&year={year}",
    )

    rj = resp.json()

    return rj["data"]

def parse_command(text: str):
    sess=None
    if "fall" in text:
        sess="fall"
    if "winter" in text:
        sess="winter"

    if sess == None:
        # Unsupported session
        pass

    ans = pat.findall(text)[0]

        
    return get_course(session=sess, subject=ans[0], course_code=ans[1])


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

class Uocourse(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.content.startswith("uo!find"):
            ans = parse_command(message.content.replace("uo!find ", ""))
            emb = discord.Embed(title=f"{ ans['course_name'] } ({ans['subject_code']}{ans['course_code']})", color=33023)

            for k, section in ans["sections"].items():
                tt = f"Section {k}"
                tv = []
                for kc, comp in section["components"].items():
                    if comp["status"] in sttt.keys():
                        st = sttt[comp["status"]]
                    else: 
                        st = "⚠️"
                    tv.append(
                        f"""
                            {st} {kc} {dayd[comp['day']]} {comp['start_time_12hr']} - {comp['end_time_12hr']}
                        """
                    )
                    
                emb.add_field(name=tt, value="".join(tv), inline=False)
            await message.channel.send(embed=emb)


intents = discord.Intents.default()
intents.message_content = True
client = Uocourse(intents=intents)
client.run(os.environ.get("UOCBOT"))