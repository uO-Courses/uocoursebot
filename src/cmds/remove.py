import discord, json
from discord.ui import Select, View

from lib.utils import embed_gen

def register_remove(tree, client, s_d, gu):
    @tree.command(name="remove", description="Remove a course")
    async def slash_04(intr01: discord.Interaction):

        uid_to_courses = s_d.utc

        userid = intr01.user.id
        await intr01.response.defer(thinking=True)
        emb = embed_gen(title="Choose which section to remove.", color = 10181046)

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
                s_d.update_utc(uid_to_courses)

                await intr01.followup.send(f"Sucessfully deleted {val}.")
                

        sel.callback = selection_callback
        view = View()
        view.add_item(sel)
        
    

        await intr01.followup.send(embed=emb, view=view)



