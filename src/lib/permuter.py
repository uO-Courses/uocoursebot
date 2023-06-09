import itertools
import math
import discord

from lib.course import Courses
from lib.course import CComponentType
from lib.data import SharedData
from lib.scheduler import ScheduleImage
from lib.utils import embed_gen

daydat = {
    "MO": 0,
    "TU": 1,
    "WE": 2,
    "TH": 3,
    "FR": 4,
    "SA": 5,
    "SU": 6
}

CURRENT_NUM = 0


class ScheduleViewer(discord.ui.View):

    def from_user_id(shared_data: SharedData, userid, term = "FALL", ):
        return ScheduleViewer(shared_data.get_courses(userid, term=term))       
         

    def __init__(self, courses):

        courses = [course.split('-') for course in courses]

        self.term = courses[0][2].lower()

        self.generate_options(courses)
        
        self.max = {k: False for k, _ in enumerate(self.selected)}

        super().__init__(timeout=100)
        

    def generate_options(self, courses):
        c = Courses()

        d = [(c(course, self.term)[0].sections[section], course) for course, section, _ in courses]

        options = []
        mandatory = []

        for sec, crs in d:
            for _, comp in sec.components.items():
                data = (f"{crs} " + " " +  comp.id, comp.start_hour, comp.start_minute, comp.end_hour, comp.end_minute, daydat[comp.day], comp.type, crs, comp)
                if comp.type == CComponentType.Lec:
                    mandatory.append(data)

        self.mandatory = mandatory

        for sec, crs in d:
            sub = {

            }
            for _, comp in sec.components.items():
                data = (f"{crs} " + " " +  comp.id, comp.start_hour, comp.start_minute, comp.end_hour, comp.end_minute, daydat[comp.day], comp.type, crs, comp)
                if not comp.type == CComponentType.Lec:
                    if self.check_if_fits(data, True):
                        if comp.type in sub.keys():
                            sub[comp.type].append(data)
                        else:
                            sub[comp.type] = [data]
                    else:
                        pass
                        #print(self.why)

            options.extend([v for _, v in sub.items()])

        selected = []

        for _ in range(len(options)):
            selected.append(-1)

        self.index = 0

        self.options = options
        self.selected = selected
        self.mandatory = mandatory
        self.total_permutations = math.prod([len(x)+1 for x in self.options])
    
    def overlaps(self, a, b):
        starta = (a[1], a[2])
        startb = (b[1], b[2])
        enda = (a[3], a[4])
        endb = (b[3], b[4])

        ##print(a[0], b[0])


        contains = lambda a, c: lambda b: a[0] <= b[0] and a[1] <= b[1] and b[0] <= c[0] and b[1] <= c[1]

        a_contains = contains(starta, enda)
        b_contains = contains(startb, endb)

        r = (a_contains(startb), a_contains(endb), b_contains(starta), b_contains(enda))
        i = a[5] == b[5]
        if any(r) and i:
            self.why += f"{a[0]} ({a[8].rday} {a[8].start_time_12hr} - {a[8].end_time_12hr}) and {b[0]} ({b[8].rday} {b[8].start_time_12hr} - {b[8].end_time_12hr}) overlap ({(starta, startb, enda, endb)}\n{r}).\n\n"

        return any(r) and i

    def check_if_fits(self, new, _pre=False):
        self.why = ""
        total = self.generate_from_selected(_pre)
        return not any([self.overlaps(new, el) for el in total])

    def generate_from_selected(self, _pre=False):
        total = [] + self.mandatory
        if not _pre:
            for i in range(len(self.selected)):
                if self.selected[i] != -1:
                    total.append(self.options[i][self.selected[i]])

        return total
    
    def generate(self):
        global CURRENT_NUM

        si = ScheduleImage()
        si.schedule(self.generate_from_selected())
        
        si.save(f"current.png")

        self.last_save = CURRENT_NUM

        CURRENT_NUM += 1

    def next(self):
        # self.options
        # self.selected

        toadd = 1

        for i in range(len(self.selected)):
            self.selected[i] += toadd
            toadd = 0
            if self.selected[i] == len(self.options[i]):
                self.selected[i] = -1
                toadd = 1

        self.index = (self.index + 1) % self.total_permutations

    def previous(self):
        # self.options
        # self.selected

        toadd = -1

        for i in range(len(self.selected)-1, -1, -1):
            self.selected[i] += toadd
            toadd = 0
            if self.selected[i] == -2:
                self.selected[i] = len(self.options[i])-1
                toadd = -1

        self.index -= 1
        if self.index < 0:
            self.index = self.total_permutations - 1

    def get_embed(self):
        emb = embed_gen(title=f"Your {self.term.capitalize()} schedule", color = 10181046)

        file = discord.File(f"current.png", filename="image.png")

        emb.set_image(url="attachment://image.png")

        return emb, file

    async def start(self, intr: discord.Interaction):

        self.intr = intr

        self.generate()

        emb, file = self.get_embed()
        
        await self.intr.followup.send(embed=emb, file=file, view=self, ephemeral=True)


    async def update(self, interaction: discord.Interaction):
        self.generate()

        emb, file = self.get_embed()

        message = await self.intr.original_response()

        await interaction.response.send_message(embed=emb, file=file, view=self, ephemeral=True)

        await message.edit(view=None)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def prev(self, interaction: discord.Interaction, button: discord.Button):
        self.previous()
        await self.update(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def nxt(self, interaction: discord.Interaction, button: discord.Button):
        self.next()
        await self.update(interaction)

    def hide_buttons(self):
        for butt in self.children:
            butt.disabled = True

    def show_buttons(self):
        for butt in self.children:
            butt.disabled = False

    async def on_timeout(self):
        message = await self.intr.original_response()

        self.hide_buttons()

        await message.edit(view=self)

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