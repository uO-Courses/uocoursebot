import requests, re, discord


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

def get_time(time):
  f = (lambda funcs, start: [(start := f(start[0] if type(start) == tuple else start)) for f in funcs])
  return ''.join([(lambda v, uname: f"{v} {uname}{ '' if v == 1 else 's'}{'' if uname == 'second' else ' '}" if v != 0 else "")(a, b) for _, a, b in f([(lambda d, uname: lambda t: ((t - (t//d)*d), (t//d), uname))(x, y) for x, y in [(86400, 'day'), (3600, 'hour'), (60, 'minute'), (1, 'second')]], time)])  

cache = {}

def embed_gen(*args, **kwargs):
    emb =  discord.Embed(*args, **kwargs)
    emb.set_footer(text="Copyright © Ann Mauduy-Decius")
    return emb

async def pretty_print_user(client, uid):
    return f"<@{uid}>"