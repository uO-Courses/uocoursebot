import discord, json
from discord.ui import Select, View

from lib.utils import parse_command, dayd, sttt, pat, embed_gen

def register_buddy(tree, client, uid_to_courses):
    @tree.command(name="buddy", description="Find people in the same sections as you", guild=discord.Object(1095372141966393364))
    async def slash_02(intr01: discord.Interaction, minimum: int = 1):
        userid = intr01.user.id

        await intr01.response.defer()

        u_to_buddy = {}
        for k, v in uid_to_courses.items():
            if userid in v:
                for id in v:
                    if id != userid:
                        if id not in u_to_buddy.keys():
                            u_to_buddy[id] = [k]
                        else:
                            u_to_buddy[id].append(k)
        
        embs = []
        emb = embed_gen(title="People who are in the same sections as you (1)", color = 10181046)
        i = 0
        n = 1

        for k, v in u_to_buddy.items():
            if len(v) >= minimum:
                u = await client.fetch_user(k)
                emb.add_field(name=u.name, value="\n".join(v))

                if i >= 24:
                    i = 0
                    n += 1
                    embs.append(emb)
                    emb = embed_gen(title=f"People who are in the same sections as you ({n})", color = 10181046)

                i += 1
        embs.append(emb)

        if emb.fields == []:
            emb.description = f"Unfortunately, no one is in {minimum} or more identical sections to you."

        await intr01.followup.send(embed=embs[0])
        for em in embs[1:-1]:
            await intr01.channel.send(embed=em)


