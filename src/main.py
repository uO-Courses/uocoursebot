
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
from lib.data import SharedData

# a course section ID should be like FRA1528-A-FALL
uid_to_courses = {
     
}

preferences = {

}

with open("utc.json", 'r') as f:
    uid_to_courses = json.loads(f.read())

with open("preferences.json", 'r') as f:
    preferences = json.loads(f.read())

s_d = SharedData(uid_to_courses, preferences)


mra = {}
    
with open("tags.json", "r") as f:
    tags = json.loads(f.read())

class Uocourse(discord.Client):
    async def on_ready(self):

        tree.copy_global_to(guild=discord.Object(776251117616234506))

        l = await tree.sync()

        print('Logged in as', self.user)
        

    async def on_message(self, message: discord.Message):

        if message.content.startswith(":addtag") and message.author.id in [443591472164503564, 218065068875579393, 331431342438875137]:
            a, b = message.content.replace(":addtag ", "").replace(" -> ", "->").split("->")
            tags[a] = b
            with open("tags.json", "f") as f:
                f.write(json.dumps(tags, indent=4))

            await message.channel.send("Successfully added tag {a}")

        for k, v in tags.items():

            if message.content.startswith(f"!{k}"):
                await message.channel.send(v, reference=message)

        if message.reference is not None:
            if message.reference.message_id in mra.keys():
                if len(message.attachments) > 0 and mra[message.reference.message_id] == message.author.id:
                    await tt(message, message.attachments, message.author.id)
                else:
                    if mra[message.reference.message_id] == message.author.id:
                        await message.channel.send("Your message does not contain a file.", reference=message)
                    else:
                        await message.channel.send("Please use /import to import your own schedule.", reference=message)


async def tt(msg_or_int, attchs: list[discord.Attachment], userid):

    uid_to_courses = s_d.utc

    ff = [await att.read() for att in attchs]
    ct = True

    try:
        res = list(itertools.chain.from_iterable([json.loads(f.decode('utf-8'))["courses"] for f in ff]))
    except:
        await msg_or_int.channel.send("Could not parse files. Are you sure you sent the right files?")
        ct = False
    if ct:
        try:
            cc = [f"{el['subject_code']}{el['course_code']}-{el['sections'][0]['label']}-{el['sections'][0]['season'].upper() }" for el in res]

        except Exception as e:
            await msg_or_int.channel.send("There was an error parsing the files")
            
            ct = False

        if ct:
            ttx = []
            for tname in cc:
                if tname in uid_to_courses:
                    if userid in uid_to_courses[tname]:
                        ttx.append(f"{tname}: You have already added this section.")
                    else:
                        uid_to_courses[tname].append(userid)
                        r = []
                        for u in uid_to_courses[tname]:
                            ue = await client.fetch_user(u)
                            r.append(ue.name)

                        rr = '\n'.join(r)
                        ttx.append(f"Succesfully added {tname.upper()}. The following people are in this section: \n{rr}.")
                else:
                    uid_to_courses[tname] = [userid]
                    ttx.append(f"Succesfully added {tname.upper()}. You are the only person who has currently selected this section.")

            await msg_or_int.channel.send("\n\n".join(ttx))
            s_d.update_utc(uid_to_courses)
            s_d.set_preference(userid, 'has_added_courses', True)
            



intents = discord.Intents.default()
intents.message_content = True
client = Uocourse(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_command_error(ctx, error):
    await ctx.send(f"{error}")

@tree.command(name="import", description="Import your schedule from uSchedule.me")
async def slash_06(intr01: discord.Interaction, file_fall: discord.Attachment=None, file_winter: discord.Attachment=None):
    tta = []
    if file_fall is not None:
        tta.append(file_fall)
    if file_winter is not None:
        tta.append(file_winter)
    
    if len(tta)==0:
        await intr01.response.send_message("First, add your courses on uSchedule for Fall and Winter.", file=discord.File('ed1eea33cb30cbee88ee5cf0a1cd9f7b.gif'))
        await intr01.channel.send("Then, go to the 'Schedules' tab and download the files.", file=discord.File("e27d13cc24a0c2d7deca203e05cab51f.gif"))
        await intr01.channel.send("Finally, reply to the next message with the files you just downloaded.", file=discord.File("43ffb39e9d4fa2eb1edc28a99d74db39.gif"))
        r = await intr01.channel.send("Please reply to this message with the files.")
        mra[r.id] = (intr01.user.id)
    else:
        await intr01.response.send_message("Processing.")
        await tt(intr01, tta, intr01.user.id)



register(tree, client, s_d)

client.run(os.environ.get("UOCBOT"))

