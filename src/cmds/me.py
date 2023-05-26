import discord 

from lib.utils import embed_gen, pretty_print_user

def register_me(tree, client, uid_to_courses, gu):
    
    @tree.command(name="profile", description="View your courses")
    async def slash_03(intr01: discord.Interaction):
        userid = intr01.user.id
        await intr01.response.defer(thinking=True)
        emb = embed_gen(title="Your courses.", color = 10181046)
        for k, v in uid_to_courses.items():
            if userid in v:
                r = []
                for u in v:
                    r.append(await pretty_print_user(client, u))

                rr = '\n'.join(r)
                emb.add_field(name=k, value=rr)
            
        await intr01.followup.send(embed=emb)
