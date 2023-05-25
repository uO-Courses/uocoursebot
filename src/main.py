
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

from cmds import register

# a course section ID should be like FRA1528-A-FALL
uid_to_courses = {
     
}

with open("utc.json", 'r') as f:
    uid_to_courses = json.loads(f.read())

class Uocourse(discord.Client):
    async def on_ready(self):
        with open("guilds.json", 'r') as f:
            g = json.loads(f.read())

        tree.copy_global_to(guild=discord.Object(g[0]))

        await tree.sync()

        print('Logged in as', self.user)

    async def on_message(self, message):
            
        pass

intents = discord.Intents.default()
intents.message_content = True
client = Uocourse(intents=intents)
tree = discord.app_commands.CommandTree(client)

register(tree, client, uid_to_courses)

client.run(os.environ.get("UOCBOT"))
