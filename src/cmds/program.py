import requests, re

from bs4 import BeautifulSoup
            
import discord

from lib.utils import dayd, sttt, embed_gen, Pagination

from lib.course import Courses

from lib.sequence import get_engineering, eng

def register_program(tree: discord.app_commands.CommandTree, client: discord.Client, uid_to_courses, gu):
    
    g = discord.app_commands.Group(name="program", description="Find your program's course sequence.")


    @g.command(name="engineering")
    @discord.app_commands.choices(program_name=[
        discord.app_commands.Choice(name=eng_name, value=eng_name)
        for eng_name in eng.keys()
    ])
    @discord.app_commands.choices(year=([discord.app_commands.Choice(name="All", value=0)] + [
        discord.app_commands.Choice(name=f"Year {n}", value=n)
        for n in range(1, 5)
    ]))
    async def slash_02(intr01: discord.Interaction, program_name: discord.app_commands.Choice[str], year: discord.app_commands.Choice[int]=0):

        year = year if type(year) is int else year.value

        await intr01.response.defer()

        rrd = get_engineering(program_name.value)

        rnames = rrd.keys()

        select = discord.ui.Select(placeholder="Select your program", options=[
            discord.SelectOption(label=n) if len(n) < 100 else discord.SelectOption(label=f"{n[0:97]}...")
            for n in rnames
        ])

        async def some_callback(intr02: discord.Interaction):

            await intr02.response.defer()

            selected = select.options[0]

            v = rrd[selected.value]

            embs = []
            y = 1
            
            for x in v:
                if year == 0 or year == y:

                    embed = embed_gen(title=f"Year {y}", color = 10181046)
                    for k, va in x.items():
                        #print(va)
                        embed.add_field(name=f"{k.capitalize()} term", value="\n".join([f"`{el}`" for el in va]), inline=False)

                    embs.append(embed)


                y+=1


            await intr02.followup.send(embeds=embs)

        select.callback = some_callback

        v = discord.ui.View()
        
        v.add_item(select)

        await intr01.followup.send(view=v)

    tree.add_command(g)

