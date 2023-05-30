from lib.utils import check_if_exists, parse_command

class Courses:

    inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super(Courses, cls).__new__(cls)

        return cls._inst
    
    def __init__(self):
        self.cache = {}

    def other_term(self, term):
        return (['winter', 'fall'] - [term])[0]

    def get_class(self, code, term):

        scode = code.upper().replace(' ', '')

        nterm = self.other_term(term)

        #// check cache

        if term in self.cache:

            if scode in self.cache[term]:
                
                return self.cache[term][scode]
        
        elif nterm in self.cache:
            
            if scode in self.cache[nterm]:

                return self.cache[nterm][scode]

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
            if term in self.cache:
                self.cache[term][scode] = res
            else:
                self.cache[term] = {
                    scode: res
                }

        return Course(res[0]), res[1:]
    
class Course:
    
    def __init__(self, ans):
        self.name = ans["course_name"]
        self.subject = ans["subject_code"]
        self.code = ans["course_code"]
        self.sections = {k: Section(v) for k, v in ans["sections"].items()}

    def components(self):
        return [c for s in self.section.values() for c in s.components.values()]
    
    def get_profs(self):
        profs = set(self.components())

        profs = list(filter(("Unknown").__ne__, profs))

        return profs

class Section:

    def __init__(self, ans):
        self.components = {k: Component(v) for k, v in ans["components"].items()}

class Component:

    def __init__(self, ans):
        self.instructor = ans["instructor"]
        self.status = ans["status"]
        self.start_time_12hr = ans["start_time_12hr"]
        self.end_time_12hr = ans["end_time_12hr"]
        self.day = ans["day"]