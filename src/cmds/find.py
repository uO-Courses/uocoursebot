import discord

from lib.utils import parse_command, dayd, sttt, year, embed_gen

def register_find(tree: discord.app_commands.CommandTree, client, uid_to_courses, gu):
    
    @tree.command(name="find", description="Find a course")
    async def slash_02(intr01: discord.Interaction, course_code: str, term: str="Fall"):
        userid = intr01.user.id
        msgtx = f"{term.lower()} {course_code.replace(' ', '')}"
        ans, b = parse_command(msgtx)
        spmsg = ""
        ff = "Fall"

        await intr01.response.defer(thinking=True)
        if ans == None and b:
            ff = "Winter"
            ans, _ = parse_command(f'winter {msgtx}')
        if ans == None:
            if "winter" in msgtx:
                ans, _ = parse_command(f'{msgtx.replace("winter", "fall")}')
                spmsg = "Course not found for Winter term but found for Fall term."
            else:
                ans, _ = parse_command(f'{msgtx.replace("fall", "winter")}')
                spmsg = "Course not found for Fall term but found for Winter term."
        if ans != None:
            if b:
                await intr01.channel.send(f"No term specified, defaulting to {ff} {year}.")
                
            if spmsg != "":
                await intr01.channel.send(spmsg)

            emb = embed_gen(title=f"{ ans['course_name'] } ({ans['subject_code']}{ans['course_code']})", color = 10181046)

            for k, section in ans["sections"].items():
                tt = f"Section {k}"
                tv = []
                profs = []
                for kc, comp in section["components"].items():
                    prof = comp["instructor"]
                    if prof not in profs:
                        profs.append(prof)
                    if comp["status"] in sttt.keys():
                        st = sttt[comp["status"]]
                    else: 
                        st = "⚠️"
                    tv.append(
                        f"""
                            {st} {kc} {dayd[comp['day']]} {comp['start_time_12hr']} - {comp['end_time_12hr']}
                        """
                    )
                emb.add_field(name=f"{tt} ({', '.join(profs)})", value="".join(tv), inline=False)
            await intr01.followup.send(ephemeral=True, embed=emb)
        else:
            await intr01.channel.send(f"Could not find specified course ({msgtx.replace('winter ', '').replace('fall ', '').upper()})")