import discord, json
from discord.ui import Select, View

from lib.utils import embed_gen

def callback_maker(sel, uid_to_courses, userid, s_d):
    async def selection_callback(intr01: discord.Interaction):
        if intr01.user.id == userid:
            await intr01.response.defer()
            val = sel.values[0]
            
            v = uid_to_courses[val]
            if userid in v:
                v.remove(userid)
            s_d.update_utc(uid_to_courses)
            s_d.set_preference(userid, 'course_selection', [])

            await intr01.followup.send(f"Sucessfully deleted {val}.")

    return selection_callback

def register_remove(tree, client, s_d, gu):
    @tree.command(name="remove", description="Remove a course")
    async def slash_04(intr01: discord.Interaction):

        uid_to_courses = s_d.utc

        userid = intr01.user.id
        await intr01.response.defer(thinking=True)

        ss = []
        for k, v in uid_to_courses.items():
            if userid in v:
                ss.append(k)


        sel = Select(
            placeholder="Choose the section to remove",
            options=[
                discord.SelectOption(label=k) for k in ss
            ]
        )          

        sel.callback = callback_maker(sel, uid_to_courses, userid, s_d)

        view = View()
        view.add_item(sel)

        await intr01.followup.send(view=view)



