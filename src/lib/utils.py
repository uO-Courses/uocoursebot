import requests, json, os, re, discord
from typing import Callable, Optional

class Pagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

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

    async def navigate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.interaction.followup.send(embed=emb)
        elif self.total_pages > 1:
            self.update_buttons()
            await self.interaction.followup.send(embed=emb, view=self)

    async def edit_page(self, interaction: discord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(embed=emb, view=self)

    def update_buttons(self):
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        if self.index <= self.total_pages//2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1

dayd = {
    "MO": "Monday",
    "TU": "Tuesday",
    "WE": "Wednesday",
    "TH": "Thursday",
    "FR": "Friday",
    "SA": "Saturday",
    "SU": "Sunday"
}

sttt = {
    "OPEN": "🟢",
    "CLOSED": "🔴"
}

year = 2023


pat = re.compile(r"(.{3})(\d{4}\d?)")

def get_course(session: str, subject: str, course_code: int, yr: int=year):
    if session.lower() == "winter":
        yr = 2024

    resp = requests.get(
        f"https://uschedule.me/api/scheduler/v1/courses/query/?school=uottawa&course_code={course_code}&subject_code={subject.upper()}&season={session.lower()}&year={yr}"
    )

    rj = resp.json()

    return rj["data"]

def parse_command(text: str):
    sess=None
    b=False
    if "fall" in text:
        sess="fall"
    if "winter" in text:
        sess="winter"

    if sess == None:
        # Unsupported session
        sess="fall"
        b = True

    ans = pat.findall(text)[0]

        
    return get_course(session=sess, subject=ans[0], course_code=ans[1]), b

def check_if_exists(course_code):
    subject_code = course_code[0:3]
    course_number = course_code[3:]
    p = requests.get(f"https://catalogue.uottawa.ca/en/courses/{subject_code.lower()}/")
    return (f"{subject_code.upper()} {course_number}" in p.text or f"{subject_code.upper()} {course_number}" in p.text)

def remember_accm(funcs, start, vars=[]):
  for f in funcs: 
    start, a, b = f(start)
    vars.append((a, b))
  return vars

def get_time(time):
  get_unit_f, print_unit = lambda d, uname: lambda t: ((t - (t//d)*d), (t//d), uname), lambda v, uname: f"{v} {uname}{ '' if v == 1 else 's'} " if v != 0 else ""
  return ''.join([print_unit(a, b) for a, b in remember_accm([get_unit_f(x, y) for x, y in [(86400, 'day'), (3600, 'hour'), (60, 'minute'), (1, 'second')]], time)])

cache = {}

def get_class(code, term): #/ -> (dict, msg, bool)

    scode = code.upper().replace(' ', '')

    if term in cache:

        if scode in cache[term]:
            
            return cache[term][scode]

    fxcode = code.replace(' ', '').upper()

    ff = term.replace(' ', '').lower()
    msgtx = f"{ff} {fxcode}"

    if len(fxcode) > 8 or not fxcode[0:3].isalpha() or not fxcode[3:7].isnumeric():
        if fxcode[0:3].isalpha() and fxcode[3:7].isnumeric():
            return None, f"Course code ({fxcode}) is invalid. Did you mean {fxcode[0:7]}?", False, msgtx, ff.upper()
        else:
            return None, f"Course code ({fxcode}) is invalid.", False, msgtx, ff.upper()
        
    if not check_if_exists(fxcode):
        return None, f"Course {fxcode} doesn't exist.", False, msgtx, ff.upper()
    
    ans, _ = parse_command(msgtx)
    spmsg = ""
    wrk = True

    if ans == None:
        if "winter" in msgtx:
            ans, _ = parse_command(f'{msgtx.replace("winter", "fall")}')
            spmsg = "Course not found for Winter term but found for Fall term."
        else:
            ans, _ = parse_command(f'{msgtx.replace("fall", "winter")}')
            spmsg = "Course not found for Fall term but found for Winter term."
    
    if ans == None:
        spmsg = f"Course not found ({fxcode})"
        wrk = False

    res = (ans, spmsg, wrk, msgtx, ff.upper())

    if wrk:
        if term in cache:
            cache[term][scode] = res
        else:
            cache[term] = {
                scode: res
            }

    return res

def embed_gen(*args, **kwargs):
    emb =  discord.Embed(*args, **kwargs)
    emb.set_footer(text="Copyright © Ann Mauduy-Decius")
    return emb

async def pretty_print_user(client, uid):
    return f"<@{uid}>"