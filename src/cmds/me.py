import discord 

from lib.utils import embed_gen

def register_me(tree, client, uid_to_courses):
    @tree.command(name="me", description="View your courses", guild=discord.Object(1095372141966393364))
    async def slash_03(intr01: discord.Interaction):
        userid = intr01.user.id
        rrr=""
        await intr01.response.defer(thinking=True)
        emb = embed_gen(title="Your courses.", color = 10181046)
        for k, v in uid_to_courses.items():
            if userid in v:
                r = []
                for u in v:
                    ue = await client.fetch_user(u)
                    r.append(ue.name)

                rr = '\n'.join(r)
                emb.add_field(name=k, value=rr)
            
        await intr01.followup.send(embed=emb)