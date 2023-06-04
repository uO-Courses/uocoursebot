import discord

from lib.utils import embed_gen

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
        embed = embed_gen(title=f"{pg[0]} ({idx+1}/{self.length})", color = 10181046)

        self.delegate_embed_generation(embed, pg[1:])

        return embed
    
    def delegate_embed_generation(self, embed, data):
        if self.mode == 0:
            return self.generate_description_mode(embed, data)
    
    def generate_description_mode(self, embed: discord.Embed, data):
        embed.description = "\n".join(data)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.intr.user:
            return True
        else:
            emb = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False
    
    async def update(self, intr):
        emb = self.get_page(self.index)

        await intr.response.edit_message(embed=emb, view=self)

    def hide_buttons(self):
        for butt in self.children:
            butt.disabled = True

    def show_buttons(self):
        for butt in self.children:
            butt.disabled = False

    def cycle_page(self, i):
        self.index = (self.index + i) % self.length
    
    def next_page(self):
        self.cycle_page(1)

    def previous_page(self):
        self.cycle_page(-1)

    async def start(self):
        emb = self.get_page(self.index)

        if self.length == 1:
            self.hide_buttons()

        await self.intr.followup.send(embed=emb, view=self)
        
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.blurple)
    async def beginning(self, interaction: discord.Interaction, button: discord.Button):
        self.index = 0
        await self.update(interaction)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.previous_page()
        await self.update(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.next_page()
        await self.update(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        self.index = self.length - 1
        await self.update(interaction)

    async def on_timeout(self):
        message = await self.intr.original_response()

        self.hide_buttons()

        await message.edit(view=self)