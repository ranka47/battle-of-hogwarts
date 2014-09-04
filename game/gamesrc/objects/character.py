"""

Template for Characters

Copy this module up one level and name it as you like, then
use it as a template to create your own Character class.

To make new logins default to creating characters
of your new type, change settings.BASE_CHARACTER_TYPECLASS to point to
your new class, e.g.

settings.BASE_CHARACTER_TYPECLASS = "game.gamesrc.objects.mychar.MyChar"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
from ev import Character as DefaultCharacter
from ev import Script
import random

class Character(DefaultCharacter):
    """
    The Character is like any normal Object (see example/object.py for
    a list of properties and methods), except it actually implements
    some of its hook methods to do some work:

    at_basetype_setup - always assigns the default_cmdset to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    def at_object_creation(self):
        self.db.score = 0
        self.db.health_max = 100
        self.db.health = self.db.health_max
        self.db.will = 100
        self.db.respawns = 0
        houses = ["Gryffindor","Hufflepuff","Slytherin","Ravenclaw"]
        self.db.house = houses[random.randint(0, len(houses) - 1)]
        self.db.dementors = 0
        self.db.spiders = 0
        self.db.willow = 0
        self.db.rodents = 0
        self.db.boggart = 0
        self.db.parallax = 0
        self.db.dragon = 0

    def respawn(self):
        self.msg("You lost a life and respawn with all your default powers")
        self.db.health = self.db.health_max
        self.db.score -= 50
        self.db.will = 100
        self.db.respawns += 1