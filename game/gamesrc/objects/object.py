"""
MUDtrix - basic objects

--------
Objects:
--------
Readable
Talking NPCs
Wand

---------
Commands:
---------
CmdRead - read readable objects
CmdTalk - talk with NPC's

---------------
List of spells:
---------------
CmdAvis
CmdArania
"""

import random, time
from django.conf import settings

from ev import Object as DefaultObject
from ev import Exit, Command, CmdSet, Script, default_cmds, search_object, utils
from contrib import menusystem
from game.gamesrc.scripts import script as mudtrix_script

BASE_CHARACTER_TYPECLASS = settings.BASE_CHARACTER_TYPECLASS

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
#   Talking NPC
#-----------------------------------------------------------------------------------
#
# Talk Command
#

class CmdTalk(default_cmds.MuxCommand):
    """
    talks to an npc

    Usage:
      talk

    This command is only available if a talkative non-player-character (NPC)
    is actually present. It will strike up a conversation with that NPC
    and give you options on what to talk about.
    """
    key = "talk"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Implements the command."

        # self.obj is the NPC this is defined on
        obj = self.obj

        self.caller.msg("(You walk up and talk to %s.)" % self.obj.key)

        # conversation is a dictionary of keys, each pointing to
        # a dictionary defining the keyword arguments to the MenuNode
        # constructor.
        conversation = obj.db.conversation
        if not conversation:
            self.caller.msg("%s says: 'Sorry, I don't have time to talk right now.'" % (self.obj.key))
            return

        # build all nodes by loading them from the conversation tree.
        menu = menusystem.MenuTree(self.caller)
        for key, kwargs in conversation.items():
            menu.add(menusystem.MenuNode(key, **kwargs))
        menu.start()


class TalkingCmdSet(CmdSet):
    "Stores the talk command."
    key = "talkingcmdset"

    def at_cmdset_creation(self):
        "populates the cmdset"
        self.add(CmdTalk())

#
# Discussion tree. See contrib.menusystem.MenuNode for the keywords.
# (This could be in a separate module too)
#

CONV = {"START": {"text": "Hello there, how can I help you?",
                  "links": ["info1", "info2"],
                  "linktexts": ["Hey, do you know what this 'Evennia' thing is all about?",
                                "What's your name, little NPC?"],
                  "keywords": None,
                  "code": None},
        "info1": {"text": "Oh, Evennia is where you are right now! Don't you feel the power?",
                  "links": ["info3", "info2", "END"],
                  "linktexts":["Sure, *I* do, not sure how you do though. You are just an NPC.",
                              "Sure I do. What's yer name, NPC?",
                              "Ok, bye for now then."],
                 "keywords": None,
                 "code": None},
        "info2": {"text": "My name is not really important ... I'm just an NPC after all.",
                 "links": ["info3", "info1"],
                 "linktexts": ["I didn't really want to know it anyhow.",
                              "Okay then, so what's this 'Evennia' thing about?"],
                 "keywords": None,
                 "code": None},
        "info3": {"text": "Well ... I'm sort of busy so, have to go. NPC business. Important stuff. You wouldn't understand.",
                 "links": ["END", "info2"],
                 "linktexts": ["Oookay ... I won't keep you. Bye.",
                               "Wait, why don't you tell me your name first?"],
                 "keywords": None,
                 "code": None},
        }


class TalkingNPC(DefaultObject):
    """
    This implements a simple Object using the talk command and using the
    conversation defined above. .
    """

    def at_object_creation(self):
        "This is called when object is first created."
        # store the conversation.
        self.db.conversation = CONV
        self.db.desc = "This is a talkative NPC."
        # assign the talk command to npc
        self.cmdset.add_default(TalkingCmdSet, permanent=True)


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

class Wand(DefaultObject):
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

class Mob(Object):
    """
    This type of mobile will roam from exit to exit at
    random intervals. Simply lock exits against the is_mob attribute
    to block them from the mob (lockstring = "traverse:not attr(is_mob)").
    """
    def at_object_creation(self):
        "This is called when the object is first created."
        #self.db.info = "This is a moving object. It moves randomly from room to room."

        self.scripts.add(mudtrix_script.IrregularEvent)
        # this is a good attribute for exits to look for, to block
        # a mob from entering certain exits.
        self.db.is_mob = True
        self.db.last_location = None
        # only when True will the mob move.
        self.db.roam_mode = True

    def announce_move_from(self, destination):
        "Called just before moving"
        self.location.msg_contents("%s drifts in the direction of %s." % (self.key, destination.key))

    def announce_move_to(self, source_location):
        "Called just after arriving"
        self.location.msg_contents("%s appears from the %s." % (self.key, source_location.key))

    def update_irregular(self):
        "Called at irregular intervals. Moves the mob."
        if self.roam_mode:
            exits = [ex for ex in self.location.exits
                                    if ex.access(self, "traverse")]
            if exits:
                # Try to make it so the mob doesn't backtrack.
                new_exits = [ex for ex in exits
                                     if ex.destination != self.db.last_location]
                if new_exits:
                    exits = new_exits
                self.db.last_location = self.location
                # execute_cmd() allows the mob to respect exit and
                # exit-command locks, but may pose a problem if there is more
                # than one exit with the same name.
                # - see Enemy example for another way to move
                self.execute_cmd("%s" % exits[random.randint(0, len(exits) - 1)].key)


#------------------------------------------------------------
#
# Enemy - mobile attacking object
#
# An enemy is a mobile that is aggressive against players
# in its vicinity. An enemy will try to attack characters
# in the same location. It will also pursue enemies through
# exits if possible.
#
# An enemy needs to have a Weapon object in order to
# attack.
#
#------------------------------------------------------------

class AttackTimer(Script):
    """
    This script is what makes an eneny "tick".
    """
    def at_script_creation(self):
        "This sets up the script"
        self.key = "AttackTimer"
        self.desc = "Drives an Enemy's combat."
        self.interval = random.randint(2, 3) # how fast the Enemy acts
        self.start_delay = True # wait self.interval before first call
        self.persistent = True

    def at_repeat(self):
        "Called every self.interval seconds."
        if self.obj.db.inactive:
            return
        #print "attack timer: at_repeat", self.dbobj.id, self.ndb.twisted_task,
        # id(self.ndb.twisted_task)
        if self.obj.db.roam_mode:
            self.obj.roam()
            #return
        elif self.obj.db.battle_mode:
            #print "attack"
            self.obj.attack()
            return
        elif self.obj.db.pursue_mode:
            #print "pursue"
            self.obj.pursue()
            #return
        
        else:
            #dead mode. Wait for respawn.
            if not self.obj.db.dead_at:
                self.obj.db.dead_at = time.time()
            if (time.time() - self.obj.db.dead_at) > self.obj.db.dead_timer:
                self.obj.reset()

class Spider(Mob):
    """
    This is a monster with health (hit points).

    Spiders can be in four modes:
       roam (inherited from Mob) - where it just moves around randomly
       battle - where it stands in one place and attacks players
       pursue - where it follows a player, trying to enter combat again
       dead - passive and invisible until it is respawned

    Upon creation, the following attributes describe the enemy's actions
      desc - description
      full_health - integer number > 0
      defeat_location - unique name or #dbref to the location the player is
                        taken when defeated. If not given, will remain in room.
      defeat_text - text to show player when they are defeated (just before
                    being whisped away to defeat_location)
      defeat_text_room - text to show other players in room when a player
                         is defeated
      win_text - text to show player when defeating the enemy
      win_text_room - text to show room when a player defeates the enemy
      respawn_text - text to echo to room when the mob is reset/respawn in
                     that room.

    """
    def at_object_creation(self):
        "Called at object creation."
        super(Spider, self).at_object_creation()

        #self.db.info = "This spider will attack players in the same room."

        # state machine modes
        self.db.roam_mode = True
        self.db.battle_mode = False
        self.db.pursue_mode = False
        self.db.dead_mode = False
        # health (change this at creation time)
        self.db.full_health = 20
        self.db.health = 20
        self.db.dead_at = time.time()
        self.db.dead_timer = 100 # how long to stay dead
        # this is used during creation to make sure the mob doesn't move away
        self.db.inactive = True
        # store the last player to hit
        self.db.last_attacker = None
        # where to take defeated enemies
        #self.db.defeat_location = "darkcell"
        self.scripts.add(AttackTimer)

    def update_irregular(self):
        "the irregular event is inherited from Mob class"
        strings = self.db.irregular_echoes
        if strings:
            self.location.msg_contents(strings[random.randint(0, len(strings) - 1)])

    def roam(self):
        "Called by Attack timer. Will move randomly as long as exits are open."

        # in this mode, the mob is healed.
        self.db.health = self.db.full_health
        players = [obj for obj in self.location.contents
                   if utils.inherits_from(obj, BASE_CHARACTER_TYPECLASS) and not obj.is_superuser]
        if players:
            # we found players in the room. Attack.
            self.db.roam_mode = False
            self.db.pursue_mode = False
            self.db.battle_mode = True

        elif random.random() < 0.2:
            # no players to attack, move about randomly.
            exits = [ex.destination for ex in self.location.exits
                                                if ex.access(self, "traverse")]
            if exits:
                # Try to make it so the mob doesn't backtrack.
                new_exits = [ex for ex in exits
                                    if ex.destination != self.db.last_location]
                if new_exits:
                    exits = new_exits
                self.db.last_location = self.location
                # locks should be checked here
                self.move_to(exits[random.randint(0, len(exits) - 1)])
            else:
                # no exits - a dead end room. Respawn back to start.
                self.move_to(self.home)

    def attack(self):
        """
        This is the main mode of combat. It will try to hit players in
        the location. If players are defeated, it will whisp them off
        to the defeat location.
        """
        last_attacker = self.db.last_attacker
        players = [obj for obj in self.location.contents
                   if utils.inherits_from(obj, BASE_CHARACTER_TYPECLASS) and not obj.is_superuser]
        if players:

            # find a target
            if last_attacker in players:
                # prefer to attack the player last attacking.
                target = last_attacker
            else:
                # otherwise attack a random player in location
                target = players[random.randint(0, len(players) - 1)]

            # try to use the weapon in hand
            attack_cmds = ("pierce", "slash")                                 #attention required
            cmd = attack_cmds[random.randint(0, len(attack_cmds) - 1)]
            self.execute_cmd("%s %s" % (cmd, target))

            # analyze result.
            if target.db.health <= 0:
                # we reduced enemy to 0 health. Whisp them off to
                # the prison room.
                tloc = search_object(self.db.defeat_location)
                tstring = self.db.defeat_text
                if not tstring:
                    tstring = "You feel your conciousness slip away ... you fall to the ground as "
                    tstring += "the spiders envelops you ...\n"
                target.msg(tstring)
                ostring = self.db.defeat_text_room
                if tloc:
                    if not ostring:
                        ostring = "\n%s envelops the fallen ... and then their body is suddenly gone!" % self.key
                        # silently move the player to defeat location
                        # (we need to call hook manually)
                    target.location = tloc[0]
                    tloc[0].at_object_receive(target, self.location)
                elif not ostring:
                    ostring = "%s falls to the ground!" % target.key
                self.location.msg_contents(ostring, exclude=[target])
                # Pursue any stragglers after the battle
                self.battle_mode = False
                self.roam_mode = False
                self.pursue_mode = True
        else:
            # no players found, this could mean they have fled.
            # Switch to pursue mode.
            self.battle_mode = False
            self.roam_mode = False
            self.pursue_mode = True

    def pursue(self):
        """
        In pursue mode, the enemy tries to find players in adjoining rooms, preferably
        those that previously attacked it.
        """
        last_attacker = self.db.last_attacker
        players = [obj for obj in self.location.contents if utils.inherits_from(obj, BASE_CHARACTER_TYPECLASS) and not obj.is_superuser]
        if players:
            # we found players in the room. Maybe we caught up with some,
            # or some walked in on us before we had time to pursue them.
            # Switch to battle mode.
            self.battle_mode = True
            self.roam_mode = False
            self.pursue_mode = False
        else:
            # find all possible destinations.
            destinations = [ex.destination for ex in self.location.exits
                                                if ex.access(self, "traverse")]
            # find all players in the possible destinations. OBS-we cannot
            # just use the player's current position to move the Enemy; this
            # might have changed when the move is performed, causing the enemy
            # to teleport out of bounds.
            players = {}
            for dest in destinations:
                for obj in [o for o in dest.contents
                           if utils.inherits_from(o, BASE_CHARACTER_TYPECLASS)]:
                    players[obj] = dest
            if players:
                # we found targets. Move to intercept.
                if last_attacker in players:
                    # preferably the one that last attacked us
                    self.move_to(players[last_attacker])
                else:
                    # otherwise randomly.
                    key = players.keys()[random.randint(0, len(players) - 1)]
                    self.move_to(players[key])
            else:
                # we found no players nearby. Return to roam mode.
                self.battle_mode = False
                self.roam_mode = True
                self.pursue_mode = False

    def at_hit(self, weapon, attacker, damage):
        """
        Called when this object is hit by an enemy's weapon
        Should return True if enemy is defeated, False otherwise.

        In the case of players attacking, we handle all the events
        and information from here, so the return value is not used.
        """

        self.db.last_attacker = attacker
        if not self.db.battle_mode:
            # we were attacked, so switch to battle mode.
            self.db.roam_mode = False
            self.db.pursue_mode = False
            self.db.battle_mode = True
            #self.scripts.add(AttackTimer)

        if not weapon.db.magic:
            # In the tutorial, the enemy is a ghostly apparition, so
            # only magical weapons can harm it.
            string = self.db.weapon_ineffective_text
            if not string:
                string = "Your weapon just passes through your enemy, causing no effect!"
            attacker.msg(string)
            return
        else:
            # an actual hit
            health = float(self.db.health)
            health -= damage
            self.db.health = health
            if health <= 0:
                string = self.db.win_text
                if not string:
                    string = "After your last hit, %s fold in on itself. " % self.key
                    string += "In a moment they pause their creepy motion. But you have a "
                    string += "feeling it is only temporarily weakened. "
                    string += "You fear it's only a matter of time before it comes into life somewhere again."
                attacker.msg(string)
                string = self.db.win_text_room
                if not string:
                    string = "After %s's last hit, %s fold in on itself. " % (attacker.name, self.key)
                    string += "In a moment they pause their creepy motion. But you have a "
                    string += "feeling it is only temporarily weakened. "
                    string += "You fear it's only a matter of time before it comes into life somewhere again."
                self.location.msg_contents(string, exclude=[attacker])

                # put mob in dead mode and hide it from view.
                # AttackTimer will bring it back later.
                self.db.dead_at = time.time()
                self.db.roam_mode = False
                self.db.pursue_mode = False
                self.db.battle_mode = False
                self.db.dead_mode = True
                self.location = None
            else:
                self.location.msg_contents("%s wails, shudders and writhes." % self.key)
        return False

    def reset(self):
        """
        If the mob was 'dead', respawn it to its home position and reset
        all modes and damage."""
        if self.db.dead_mode:
            self.db.health = self.db.full_health
            self.db.roam_mode = True
            self.db.pursue_mode = False
            self.db.battle_mode = False
            self.db.dead_mode = False
            self.location = self.home
            string = self.db.respawn_text
            if not string:
                string = "%s fades into existence from out of thin air. It's looking pissed." % self.key
                self.location.msg_contents(string)