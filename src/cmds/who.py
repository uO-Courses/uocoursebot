import discord

from lib.utils import embed_gen, pretty_print_user
from lib.data import SharedData

def register_who(tree, client, s_d: SharedData, gu):
    
    @tree.command(name="who", description="View who is enrolled in a class")
    async def slash_03(intr01: discord.Interaction, course_code: str):

        uid_to_courses = s_d.utc

        cc = course_code.replace(" ", "").upper()
        await intr01.response.defer(thinking=True)
        emb = embed_gen(title=f"People enrolled in {cc}", color = 10181046)
        [emb.add_field(name=cn, value="\n".join(await s_d.get_enrolled_in(lambda x: pretty_print_user(client, x), cn))) for cn in list(filter(lambda x: cc in x, [k for k in uid_to_courses.keys()]))]


        await intr01.followup.send(embed=emb)