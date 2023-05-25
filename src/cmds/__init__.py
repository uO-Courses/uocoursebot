from . import add, find, me, who, remove

def register(tree, bot, utc):
    add.register_add(tree, bot, utc)
    find.register_find(tree, bot, utc)
    me.register_me(tree, bot, utc)
    who.register_who(tree, bot, utc)
    remove.register_remove(tree, bot, utc)