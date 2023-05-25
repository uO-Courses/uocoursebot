import requests, json, os, re, discord

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

def embed_gen(*args, **kwargs):
    emb =  discord.Embed(*args, **kwargs)
    emb.set_footer(text="Copyright © Ann Mauduy-Decius")
    return emb