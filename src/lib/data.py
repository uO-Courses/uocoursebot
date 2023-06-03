import json

class SharedData:
    def __init__(self, utc, pref):
        self.utc = utc
        self.pref = pref
        self.defaults = {
            'has_added_courses': False
        }

    def update_utc(self, uid_to_courses):
        with open("utc.json", 'w') as f:
            f.write(json.dumps(uid_to_courses, indent=4))

    def get_preference(self, userid, preference_name):
        if userid in self.pref.keys():
            if preference_name in self.pref[userid]:
                return self.pref[userid][preference_name]
        return self.defaults[preference_name]

    def set_preference(self, userid, preference_name, value):
        if userid in self.pref.keys():
            self.pref[userid][preference_name] = value
        else:
            self.pref[userid] = {preference_name: value}

        with open("preferences.json", 'w') as f:
            f.write(json.dumps(self.pref, indent=4))