
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

import requests, json, os, re, itertools
import discord
from discord.ui import Select, View

from cmds import register

# a course section ID should be like FRA1528-A-FALL
uid_to_courses = {
     
}

with open("utc.json", 'r') as f:
    uid_to_courses = json.loads(f.read())

mra = {}

class Uocourse(discord.Client):
    async def on_ready(self):

        tree.copy_global_to(guild=discord.Object(776251117616234506))

        l = await tree.sync()

        print('Logged in as', self.user)

    async def on_message(self, message: discord.Message):
        if message.reference is not None:
            if message.reference.message_id in mra.keys():
                if len(message.attachments) > 0 and mra[message.reference.message_id] == message.author.id:
                    ff = [await att.read() for att in message.attachments]
                    ct = True

                    try:
                        res = list(itertools.chain.from_iterable([json.loads(f.decode('utf-8'))["courses"] for f in ff]))
                    except:
                        await message.channel.send("Could not parse files. Are you sure you sent the right files?", reference=message)
                        ct = False
                    if ct:
                        try:
                            cc = [f"{el['subject_code']}{el['course_code']}-{el['sections'][0]['label']}-{el['sections'][0]['season'].upper() }" for el in res]

                        except Exception as e:
                            await message.channel.send("There was an error parsing the files")
                            
                            ct = False

                        if ct:
                            dat = mra.pop(message.reference.message_id)
                            userid = message.author.id
                            ttx = []
                            for tname in cc:
                                if tname in uid_to_courses:
                                    if userid in uid_to_courses[tname]:
                                        ttx.append(f"{tname}: You have already added this section.")
                                    else:
                                        uid_to_courses[tname].append(userid)
                                        r = []
                                        for u in uid_to_courses[tname]:
                                            ue = await self.fetch_user(u)
                                            r.append(ue.name)

                                        rr = '\n'.join(r)
                                        ttx.append(f"Succesfully added {tname.upper()}. The following people are in this section: \n{rr}.")
                                else:
                                    uid_to_courses[tname] = [userid]
                                    ttx.append(f"Succesfully added {tname.upper()}. You are the only person who has currently selected this section.")

                            await message.channel.send("\n\n".join(ttx))
                            with open("utc.json", 'w') as f:
                                f.write(json.dumps(uid_to_courses, indent=4))
                else:
                    await message.channel.send("Your message does not contain a file.", reference=message)


intents = discord.Intents.default()
intents.message_content = True
client = Uocourse(intents=intents)
tree = discord.app_commands.CommandTree(client)

@tree.command(name="import", description="Import your schedule from uSchedule.me")
async def slash_06(intr01: discord.Interaction):
    await intr01.response.send_message("First, add your courses on uSchedule for Fall and Winter.", file=discord.File('ed1eea33cb30cbee88ee5cf0a1cd9f7b.gif'))
    await intr01.channel.send("Then, go to the 'Schedules' tab and download the files.", file=discord.File("e27d13cc24a0c2d7deca203e05cab51f.gif"))
    await intr01.channel.send("Finally, reply to the next message with the files you just downloaded.", file=discord.File("43ffb39e9d4fa2eb1edc28a99d74db39.gif"))
    r = await intr01.channel.send("Please reply to this message with the files.")
    mra[r.id] = (intr01.user.id)

register(tree, client, uid_to_courses)

client.run(os.environ.get("UOCBOT"))
