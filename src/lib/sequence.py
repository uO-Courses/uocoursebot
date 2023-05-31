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

#// Honours BSc in Biochemistry 
eng_link = lambda n: f"https://www.uottawa.ca/faculty-engineering/undergraduate-studies/programs/{n}/course-sequence"

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