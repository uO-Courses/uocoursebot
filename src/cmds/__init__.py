from . import add, find, me, who, remove, buddy, adm, prof, program, schedule
import json

def register(tree, bot, utc):
    
    with open("guilds.json", 'r') as f:
        g = json.loads(f.read())

    add.register_add(tree, bot, utc, g)
    find.register_find(tree, bot, utc, g)
    me.register_me(tree, bot, utc, g)
    who.register_who(tree, bot, utc, g)
    remove.register_remove(tree, bot, utc, g)
    buddy.register_buddy(tree, bot, utc, g)
    adm.register_adm(tree, bot, utc, g)
    prof.register_prof(tree, bot, utc, g)
    program.register_program(tree, bot, utc, g)
    schedule.register_schedule(tree, bot, utc, g)