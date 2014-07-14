"""
MUDtrix - basic objects

Objects:
Readable
Climbable
Wand

Commands:
List of spells
"""
from ev import Object as DefaultObject
from ev import Exit, Command, CmdSet, Script
import random

#-----------------------------------------------------------------------
# Object class is base class for all other objects
#-----------------------------------------------------------------------
class Object(DefaultObject):
    """
    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved to
                           database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     dbobj (Object, read-only) - link to database model. dbobj.typeclass points
                                  back to this class
     typeclass (Object, read-only) - this links back to this class as an
                         identified only. Use self.swap_typeclass() to switch.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     player (Player) - controlling player (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       player above)
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     sessions (list of Sessions, read-only) - returns all sessions connected
                       to this object
     has_player (bool, read-only)- will only return *connected* players
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                             self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
                             a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, player=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get()      - this is called just before the command handler
                            requests a cmdset from this object
     at_pre_puppet(player)- (player-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (player-controlled objects only) called just
                            after completing connection player<->object
     at_pre_unpuppet()    - (player-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(player) - (player-controlled objects only) called just
                            after disconnecting player<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_before_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_before_traverse(traversing_object)                 - (exit-objects only)
                              called just before an object traverses this object
     at_after_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

     """
    pass

#--------------------------------------------------------------------------------
# Readable objects : The objects one can 'read'
#--------------------------------------------------------------------------------
class CmdRead(Command):
    """
    Usage:
      read [obj]

    Read some text.
    """

    key = "read"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Implement the read command."
        if self.args:
            obj = self.caller.search(self.args.strip())
        else:
            obj = self.obj
        if not obj:
            return
        # we want an attribute read_text to be defined.
        readtext = obj.db.readable_text
        if readtext:
            string = "You read {C%s{n:\n  %s" % (obj.key, readtext)
        else:
            string = "There is nothing to read on %s." % obj.key
        self.caller.msg(string)

class CmdSetReadable(CmdSet):
    "CmdSet for readables"
    def at_cmdset_creation(self):
        "called when object is created."
        self.add(CmdRead())

class Readable(Object):
    """
    This object defines some attributes and defines a read method on itself.
    """
    def at_object_creation(self):
        "Called when object is created"
        super(Readable, self).at_object_creation()
        self.db.readable_text = "There is no text written on %s." % self.key
        # define a command on the object.
        self.cmdset.add_default(CmdSetReadable, permanent=True)



#-----------------------------------------------------------------------------------
#   Spells - Wand class, spell commands and cmdset
#-----------------------------------------------------------------------------------
#
# Spells are a set of commands which share common properties like follows
#  - Spells work only if the person trying them has a wand,
#  - The probability of all spells increase as time passes by,
#  - All spells work only after they are 'learnt'.
#
#-----------------------------------------------------------------------------------


#class Spell(default_cmds.MuxCommand):
#    This is the base command for all the spells.
#    A thought for later is that this can be used to add to Cmdset all the spells at once.
#    pass

class CmdSetSpell(CmdSet):
    "Holds the attack command."
    def at_cmdset_creation(self):
        "called at first object creation."
        self.add(CmdAvis())
        self.add(CmdArania())

class Wand(Object):
    """
    This defines the wand which is used for spells.

    Important attributes - set at creation
          hit - chance(or probability) to hit (0-1).
                This can be used for changing probability of all spells depending on
                score of the player
    """
    def at_object_creation(self):
        "Called at first creation of the object"
        super(Wand, self).at_object_creation()
        self.db.hit = 0.4    # hit chance
        self.db.magic = False
        self.cmdset.add_default(CmdSetSpell, permanent=True)

    def reset(self):
        """
        When reset, the wand is simply deleted, unless it has a place
        to return to.
        """
        if self.location.has_player and self.home == self.location:
            self.location.msg_contents("%s suddenly and magically fades into nothingness, as if it was never there ..." % self.key)
            self.delete()
        else:
            self.location = self.home


#---------------------------------------------------------------------------------
# List of spells
#---------------------------------------------------------------------------------
# Avis - conjures a flock of birds from the tip of wand.
#---------------------------------------------------------------------------------

class CmdAvis(Command):
    """
    conjures a flock of birds from the tip of wand.

    Usage:
    avis

    """
    key = "avis"
    aliases = ["Avis"]
    locks = "cmd:holds()"
    help_category = "Spells"

    def func(self):
        "Actual function"
        hit = float(self.obj.db.hit) * 1.5      # increased the probability of hitting because this is an easy spell.

        if random.random() <= hit:
           self.caller.msg("A flock of birds emerge from your wand. They fly away noisily into nowhere...")
           self.caller.location.msg_contents("A heavy cluttering noise distracts you. You see a flock of birds "+
                                       "emerging from {c%s{n's wand. They fly away into nowhere..." % 
                                                           (self.caller), exclude=[self.caller])
        else:
           self.caller.msg("You said your spell but nothing happens! Don't worry, say it again with all your heart.")

#---------------------------------------------------------------------------------
# Arania Exumai - Kills or attacks Spiders
#---------------------------------------------------------------------------------

class CmdArania(Command):
    """
    attack spiders

    Usage:
    Arania Exumai (aliases: arania)

    Used to attack and kill huge clusters of spiders
    """
    key = "arania"
    aliases = ["Arania Exumai"]
    locks = "cmd:holds()"
    help_category = "Spells"

    def func(self):
        "Actual function"
        hit = float(self.obj.db.hit)*1.2    # medium difficulty

        if random.random() <= hit:
            self.caller.msg("A {yblast of light{n apears from the tip of the wand.")
            self.caller.location.msg_contents("A {yblast of light{n appears from {c%s{n's wand" %
                                                        (self.caller), exclude=[self.caller])
        else:
            self.caller.msg("You said your spell but nothing happens! Don't worry, say it with all your heart.")

#---------------------------------------------------------------------------------