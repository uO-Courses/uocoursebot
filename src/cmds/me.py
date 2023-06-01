import discord 

from lib.utils import embed_gen

def register_me(tree, client, s_d, gu):
    
    @tree.command(name="profile", description="View your courses")
    async def slash_03(intr01: discord.Interaction, user: discord.User=None):

        uid_to_courses = s_d.utc

        userid = intr01.user.id

        if user != None:
            userid = user.id

        await intr01.response.defer(thinking=True)
        fall = embed_gen(title="Your Fall courses.", color = 10181046)
        winter = embed_gen(title="Your Winter courses", color = 10181046)
        for k, v in uid_to_courses.items():
            if userid in v:
                r = []
                for u in v:
                    r.append(f"<@{u}>")#//await pretty_print_user(client, u))

                rr = '\n'.join(r)
                if "WINTER" in k:
                    winter.add_field(name=k.replace("-WINTER", ""), value=rr)
                else: 
                    fall.add_field(name=k.replace("-FALL", ""), value=rr)
            
        await intr01.followup.send(embeds=[fall, winter])
