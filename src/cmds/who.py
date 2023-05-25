import discord

from lib.utils import embed_gen

def register_who(tree, client, uid_to_courses, gu):
    
    @tree.command(name="who", description="View who is enrolled in a class")
    async def slash_03(intr01: discord.Interaction, course_code: str):
        i = 0
        cc = course_code.replace(" ", "").upper()
        await intr01.response.defer(thinking=True)
        emb = embed_gen(title=f"People enrolled in {cc}", color = 10181046)
        for k, v in uid_to_courses.items():
            if cc in k:
                r = []
                for u in v:
                    ue = await client.fetch_user(u)
                    r.append(f"{ue.name}#{ue.discriminator}")

                rr = '\n'.join(r)
                emb.add_field(name=k, value=rr)

        await intr01.followup.send(embed=emb)