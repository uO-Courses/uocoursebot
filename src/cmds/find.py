import discord

from lib.utils import dayd, sttt, embed_gen, Pagination

from lib.course import Courses


def register_find(tree: discord.app_commands.CommandTree, client: discord.Client, uid_to_courses, gu):
    
    @tree.command(name="find", description="Find a course")
    async def slash_02(intr01: discord.Interaction, course_code: str, term: str="Fall"):
        cs = Courses()

        await intr01.response.defer()

        course, spmsg, worked, _, _ = cs(course_code, term)

        if worked:
            if spmsg != "":
                intr01.channel.send(spmsg)

            emb = embed_gen(title=f"{ course.name } ({course.subject}{course.code})", color = 10181046)
            
            ttl = 0

            tttv = []

            for k, section in course.sections.items():
            
                tt = f"Section {k}"
                tv = []
                profs = []
                for kc, comp in section.components.items():
                    prof = comp.instructor
                    if prof not in profs:
                        profs.append(prof)
                    if comp.status in sttt.keys():
                        st = sttt[comp.status]
                    else: 
                        st = "⚠️"
                    tv.append(
                        f"""
{st} {kc} {dayd[comp.day]} {comp.start_time_12hr} - {comp.end_time_12hr}
                        """
                    )

                ms  = "\n".join(tv)

                ttl+=len(ms)

                emb.add_field(name=f"{tt} ({', '.join(profs)})", value=ms, inline=False)

                x=800
                res=[ms[y-x:y] for y in range(x, len(ms)+x,x)]

                tttv.extend(res)

            if ttl>4000:

                per_page = 3
                lst = tttv
                async def get_page(page: int):
                    emb = embed_gen(title=f"{ course.name } ({course.subject}{course.code})", color = 10181046)
                    emb.description = ""
                    offset = (page-1) * per_page
                    for el in lst[offset:offset+per_page]:
                        emb.description += f"{el}\n"
                    n = Pagination.compute_total_pages(len(lst), per_page)
                    emb.set_footer(text=f"Page {page} of {n}")
                    return emb, n
                
                await Pagination(intr01, get_page).navigate()


            else:
                await intr01.followup.send(embed=emb)
        else:
            await intr01.followup.send(spmsg)