import discord

from lib.utils import dayd, sttt, embed_gen, Pagination

from lib.course import Courses

class Embedinator(discord.ui.View):

    def __init__(self, interaction: discord.Interaction, data, mode=0, **kwargs):
        # modes
        #---
        # 0: data should be a list of tuples,
        # first element of the tuple is the title
        # and the rest is put in the description.
        #---
        # 
        self.index = 0
        self.length = len(data)
        self.data = data
        self.options = dict(kwargs)
        self.mode = mode
        self.intr = interaction
        super().__init__(timeout=100)

    def get_page(self, idx):
        pg = self.data[idx]
        embed = embed_gen(title=f"{pg[0]} ({idx+1}/{self.length})")

        self.delegate_embed_generation(embed, pg[1:])

        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False
    
    async def update(self):
        emb = self.get_page(self.index)

        await self.intr.response.edit_message(embed=emb, view=self)

    def cycle_page(self, i):
        self.index = (self.index + i) % self.length
    
    def next_page(self):
        self.cycle_page(1)

    def previous_page(self):
        self.cycle_page(-1)

    async def start(self):
        emb = self.get_page(self.index)

        await self.intr.followup.send(embed=emb, view=self)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.previous_page()
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.next_page()
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        self.index = self.length - 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        self.index = 0
        await self.edit_page(interaction)

    async def on_timeout(self):
        message = await self.interaction.original_response()
        await message.edit(view=None)

    def delegate_embed_generation(self, embed, data):
        if self.mode == 0:
            return self.generate_description_mode(embed, data)
    
    def generate_description_mode(self, embed: discord.Embed, data):
        embed.description = "\n".join(data)
        


def register_find(tree: discord.app_commands.CommandTree, client: discord.Client, uid_to_courses, gu):
    
    @tree.command(name="find", description="Find a course")
    @discord.app_commands.choices(term=[
        discord.app_commands.Choice(name='Fall', value='Fall'),
        discord.app_commands.Choice(name='Winter', value='Winter')
    ])
    async def slash_02(intr01: discord.Interaction, course_code: str, term: discord.app_commands.Choice[str]="Fall"):
        cs = Courses()

        term = term if type(term) is str else term.value

        await intr01.response.defer()

        course, spmsg, worked, _, _ = cs(course_code, term)

        if worked:
            if spmsg != "":
                intr01.channel.send(spmsg)
            
            ms = []

            for _, section in course.sections.items():
            
                tv = ["Section {k}"]
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
                        f"{st} {kc} {dayd[comp.day]} {comp.start_time_12hr} - {comp.end_time_12hr}"
                    )
                    

                ms.append(tuple(tv))

            
            embd = Embedinator(intr01, ms)

            await embd.start()

        else:
            await intr01.followup.send(spmsg)