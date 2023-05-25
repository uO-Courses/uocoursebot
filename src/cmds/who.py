import discord

from lib.utils import embed_gen, pretty_print_user

def register_who(tree, client, uid_to_courses, gu):
    
    @tree.command(name="who", description="View who is enrolled in a class")
    async def slash_03(intr01: discord.Interaction, course_code: str):
        cc = course_code.replace(" ", "").upper()
        await intr01.response.defer(thinking=True)
        emb = embed_gen(title=f"People enrolled in {cc}", color = 10181046)
        for k, v in uid_to_courses.items():
            if cc in k:
                r = []
                for u in v:
                    r.append(await pretty_print_user(client, u))

                rr = '\n'.join(r)
                emb.add_field(name=k, value=rr)

        await intr01.followup.send(embed=emb)