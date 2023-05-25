import discord, json
from discord.ui import Select, View

from lib.utils import parse_command, dayd, sttt

def register_remove(tree, client, uid_to_courses):
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



