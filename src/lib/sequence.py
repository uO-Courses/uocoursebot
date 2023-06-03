from bs4 import BeautifulSoup
import requests, re

pat = re.compile(r"(.{3}.?\d{4}\d?)")

### Engineering 
##! Programs
eng = {name: '-'.join(name.split(" ")[0:2]).lower() for name in [
    "Biomedical Mechanical Engineering",
    "Civil Engineering",
    "Computer Science",
    "Electrical Engineering",
    "Multidisciplinary Design",
    "Chemical Engineering",
    "Computer Engineering",
    "Data Science",
    "Mechanical Engineering",
    "Software Engineering"
]}

### Science
##! Programs
sci = {
    name: '-'.join(name.split(" ")).lower() for name in [
        "Biochemistry",
        "Biology",
        "Biopharmaceutical Science",
        "Environmental Geoscience",
        "Life Sciences",
        "Mathematic Economics",
        "Physics",
        "Statistics",
        "Biomedical Science",
        "Chemistry",
        "Environmental Science",
        "Geology",
        "Mathematics",
        "Ophtalmic Medical Technology"
    ]
} | {
    "Mathematic and Economics": "mathematic-economics",
    "Music and Science": "music-science",
    "Biochemistry and Chemical Engineering": "biochemistry-chemical-engineering",
    "Physics and Electrical Engineering": "physics-electrical-engineering"
}

eng_link = lambda n: f"https://www.uottawa.ca/faculty-engineering/undergraduate-studies/programs/{n}/course-sequence"
sci_link = lambda n: f"https://www.uottawa.ca/faculty-science/programs/undergraduate/{n}/course-sequences"

def get_engineering(program_name: str):
    l = eng_link(eng[program_name])
    r = requests.get(l)
    soup = BeautifulSoup(r.text, 'html.parser')
    r = [s.contents[0] for s in soup.find_all("h3", ["headline--3"])]
    r1 = [s.find_all("tbody")[0] for s in soup.find_all("section", ["tabs-with-content"])]

    rrd = {}

    if len(r) != 0:
        #//print(r[1:])
        #//print(r1)
        for i in range(len(r1)):
            if not "Minor" in r[i+1]:
                r2 = [{"fall": [ss.get_text() for ss in (s.find_all("td"))[0].find_all("li")], "winter": [ss.get_text() for ss in (s.find_all("td"))[1].find_all("li")]} for s in r1[i].find_all("tr")]
                for xx in r2:
                    for kx, vx in xx.items():
                        for ind in vx:
                            if len(x := pat.findall(ind)) > 0:
                                if any(x[0] in el and "Either" in el for el in vx) and "Either" not in ind:
                                    vx.remove(ind)
                                elif "Either" in ind:
                                    chr = '\r'
                                    xx[kx] = map(lambda x: x if not "Either" in x else "\n".join(["Either: "] + [f".    {el.strip()}" for el in x.split('\n')[1:-1]]), vx)
                            

                rrd[r[i+1]] = r2

    return rrd

def get_science(program_name: str):
    l = sci_link(sci[program_name])
    r = requests.get(l)
    soup = BeautifulSoup(r.text, 'html.parser')
    r = [s.contents[0] for s in soup.find_all("span", ["faq--headline"])]
    r1 = [s.find_all("tbody")[0] for s in soup.find_all("table", ["rich-text__table"])]

    rrd = {}

    if len(r) != 0:

        for i in range(len(r1)):
            if not "Minor" in r[i] and not "Major" in r[i]:
                r2 = [{"fall": ['・' + ss.get_text() for ss in (s.find_all("td"))[0].find_all("li")], "winter": ['・' + ss.get_text() for ss in (s.find_all("td"))[1].find_all("li")]} for s in r1[i].find_all("tr")]
                for xx in r2:
                    for kx, vx in xx.items():
                        for ind in vx:
                            if len(x := pat.findall(ind)) > 0:
                                if any(x[0] in el and ("Either" in el or "from" in el) for el in vx) and "Either" not in ind:
                                    vx.remove(ind)
                                elif "Either" in ind or "from" in ind:
                                    chr = '\r'
                                    xx[kx] = map(lambda x: x if (not "Either" in x and not "from" in x) else "\n".join(["Either: "] + [f".    {el.strip()}" for el in x.split('\n')[1:-1]]), vx)
                            

                rrd[r[i]] = r2

    return rrd

