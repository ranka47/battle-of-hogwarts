"""
Example command module template

Copy this module up one level to gamesrc/commands/ and name it as
befits your use.  You can then use it as a template to define your new
commands. To use them you also need to group them in a CommandSet (see
examples/cmdset.py)

"""

from ev import Command as BaseCommand
from ev import default_cmds
from ev import create_object
from ev import utils
from ev import Object as DefaultObject
from ev import managers


class Command(BaseCommand):
    """
    Inherit from this if you want to create your own
    command styles. Note that Evennia's default commands
    use MuxCommand instead (next in this module)

    Note that the class's __doc__ string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    """
    # these need to be specified

    key = "MyCommand"
    aliases = ["mycmd", "myc"]
    locks = "cmd:all()"
    help_category = "General"

    # auto_help = False      # uncomment to deactive auto-help for this command.
    # arg_regex = r"\s.*?|$" # optional regex detailing how the part after
                             # the cmdname must look to match this command.

    # (we don't implement hook method access() here, you don't need to
    #  modify that unless you want to change how the lock system works
    #  (in that case see src.commands.command.Command))

    def at_pre_cmd(self):
        """
        This hook is called before self.parse() on all commands
        """
        pass

    def parse(self):
        """
        This method is called by the cmdhandler once the command name
        has been identified. It creates a new set of member variables
        that can be later accessed from self.func() (see below)

        The following variables are available to us:
           # class variables:

           self.key - the name of this command ('mycommand')
           self.aliases - the aliases of this cmd ('mycmd','myc')
           self.locks - lock string for this command ("cmd:all()")
           self.help_category - overall category of command ("General")

           # added at run-time by cmdhandler:

           self.caller - the object calling this command
           self.cmdstring - the actual command name used to call this
                            (this allows you to know which alias was used,
                             for example)
           self.args - the raw input; everything following self.cmdstring.
           self.cmdset - the cmdset from which this command was picked. Not
                         often used (useful for commands like 'help' or to
                         list all available commands etc)
           self.obj - the object on which this command was defined. It is often
                         the same as self.caller.
        """
        pass

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
         by the cmdhandler right after self.parser() finishes, and so has access
         to all the variables defined therein.
        """
        self.caller.msg("Command called!")

    def at_post_cmd(self):
        """
        This hook is called after self.func().
        """
        pass


class MuxCommand(default_cmds.MuxCommand):
    """
    This sets up the basis for a Evennia's 'MUX-like' command
    style. The idea is that most other Mux-related commands should
    just inherit from this and don't have to implement parsing of
    their own unless they do something particularly advanced.

    A MUXCommand command understands the following possible syntax:

      name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]

    The 'name[ with several words]' part is already dealt with by the
    cmdhandler at this point, and stored in self.cmdname. The rest is stored
    in self.args.

    The MuxCommand parser breaks self.args into its constituents and stores them
    in the following variables:
      self.switches = optional list of /switches (without the /)
      self.raw = This is the raw argument input, including switches
      self.args = This is re-defined to be everything *except* the switches
      self.lhs = Everything to the left of = (lhs:'left-hand side'). If
                 no = is found, this is identical to self.args.
      self.rhs: Everything to the right of = (rhs:'right-hand side').
                If no '=' is found, this is None.
      self.lhslist - self.lhs split into a list by comma
      self.rhslist - list of self.rhs split into a list by comma
      self.arglist = list of space-separated args (including '=' if it exists)

      All args and list members are stripped of excess whitespace around the
      strings, but case is preserved.
      """

    def func(self):
        """
        This is the hook function that actually does all the work. It is called
        by the cmdhandler right after self.parser() finishes, and so has access
        to all the variables defined therein.
        """
        # this can be removed in your child class, it's just
        # printing the ingoing variables as a demo.
        super(MuxCommand, self).func()

class CmdScore(Command):
    """
    add to and see the score of a player

    Usage:
    score <player> [<+/=> <value>]

    Example:
        score <player> = <value>    - To set score to a particular value
        score <player> + <value>    - To add a value to the score
        score <player>              - To display the score of the player

    This is used to set, view and add to the score of a player. But the command needs "Builders" access.
    """
    key = "score"
    help_category = "General"

    def parse(self):
        "We do some parsing here"
        args = self.args
        name, propaddval, propsetval = None, None, None
        if "+" in args:
            args, propaddval = [part.strip() for part in args.rsplit("+", 1)]
        elif "=" in args:
            args, propsetval = [part.strip() for part in args.rsplit("=", 1)]
        self.name = args
        # if no name, value is meaningless
        self.propaddval = propaddval if self.name else None
        self.propsetval = propsetval if self.name else None

    def func(self):
        "Actual function"
        caller = self.caller
        # We do some Validation here
        # If argument or name is not given, then display Usage
        if not self.args or not self.name:
            caller.msg("Usage: score <player> [= <value>]")
            return

        # Search for the player name    
        player = caller.search(self.name)
        # If player is not found, it automatically returns an error message
        if not player:
            return
            
        # If no value we just display the score of the player
        if not self.propaddval and not self.propsetval:
            caller.msg("The current score of %s is %s" %
                              (player.key, player.attributes.get("score", default="N/A")))
            return

        # Set score to value
        if not self.propaddval:
            # Check if value is an integer
            if not self.propsetval.isdigit():
                caller.msg("The value entered is not an integer")
                return
            player.attributes.add("score", int(self.propsetval))
            caller.msg("Set score of %s to %s" % 
                              (player.key, self.propsetval))
            return

        # Add to value to existing score
        # check if value is an integer
        if not self.propaddval.isdigit():
            caller.msg("The value entered is not an integer")
            return
        currentscore = player.attributes.get("score", default=0)
        resultscore = int(self.propaddval) + currentscore
        player.attributes.add("score", resultscore)
        caller.msg("Added %s to current score of %s." % 
                          (self.propaddval, self.key))
        return

#--------------------------------------------------------------------------------------------------------------
# House - Reveals the house of the targetted player
#--------------------------------------------------------------------------------------------------------------

class CmdHouse(Command):
    """
    This command will reveal the house of the other player

    Usage
    house <playername>
    """
    key = "house"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if self.args:
            obj = self.caller.search(self.args.strip())
        else:
            obj = self.obj
        if not obj:
            return
        self.caller.msg("{c%s{n's house is {y%s{n." % (obj,obj.db.house))

#---------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------
# Status - Displays the one's own health, will and score
#-----------------------------------------------------------------------

class CmdStatus(Command):
    """
    This command will print the attributes like health, will
    and score of the player.

    Usage
    status
    """
    key = "status"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if(self.caller.db.health or self.caller.db.will or self.caller.db.score):
            self.caller.msg("{gYour Status:\n")
            if self.caller.db.health:
                self.caller.msg("{wHealth  : {y%d{n" % (self.caller.db.health))
            if self.caller.db.will:
                self.caller.msg("{wWill    : {y%d{n" % (self.caller.db.will))
            if self.caller.db.score:
                self.caller.msg("{wScore   : {y%d{n" % (self.caller.db.score))
            if self.caller.db.respawns:
                self.caller.msg("{rRespawns: {y%d{n" % (self.caller.db.respawns))
        else:
            self.caller.msg("{rNo health, will or score attributes. Contact your administrator.{n")


#-----------------------------------------------------------------------
# Remind - Reminds player of the puzzles to the spells 
#-----------------------------------------------------------------------

class CmdRemind(Command):
    """
    This command will print the puzzles of the spells.

    Usage:
    remind <number>

    number is the section of puzzles you want to print
    """
    key = "remind"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: remind <number>      ; number refers to the section of the puzzles.")
            return
        if self.args == " 1":
            string = "{cPuzzle(1){n\n"
            string+= "{wTwo Word Spell.\n"
            string+= "{wFirst word has two parts.\n"
            string+= "{wLast part of the first matches to the last half of my name not surname.\n"
            string+= "{wWhat remains of the first has four parts with an alphabet in each.\n"
            string+= "{wFirst and third part is same as the first of the alphabets (Muggles' Nursery English) and second-third-fourth would be known if you had typed ran to escape (which is wrong) being a coward like a chicken runs doing buc buc buc buc buc buc!!!\n"
            string+= "{wSecond of the spell comes with an ex and a u and also an o.{n\n"
            string+= "{gDisarming Charm{n - Causes whatever the victim is holding to fly away, knocks down the opponent if used forcefully.\n"
            string+= "YP IDR YJR D[R;; DSU\n"
            string+= "{wRC[R;;P ST,S{n\n"
            string+= "{gPatronus Charm{n - It is defensive spell which will take form a Patronus (it is an animal form which would depict your character precisely) from all your positive emotions' energy. Can be used against Lethifolds and Dementors.\n"
            string+= "YP IDR YJR D[R;; DSU\n"
            string+= "{wRC[RVYP [SYTPMID{n\n"
        elif self.args == " 2":
            string = "{cPuzzle(2){n\n"
            string+= "{gBird-Conjuring Spell{n: Seems a normal spell but has the ability to take you out of big problems, mind that. It conjures (causes to appear) a flock (group) of birds from the tip of the caster's (one who is telling the spell) wand. CAN ALSO MAKE some DEADLY SPELL OR MONSTERS GET DISTRACTED FROM YOU AS THEY IT DEFLECTS TOWARDS THE BIRDS.\n"
            string+= "{wIt is of four letter.\n"
            string+= "{wFirst shows itself the first when you start learning English from Nursery..\n"
            string+= "{wSecond appears through your fingers when you win.\n"
            string+= "{wThird appears when you always address your ownself.\n"
            string+= "{wFourth appears, will mostly appear if you say something in plural.{n\n"
            string+= "{gLevitation Spell{n: To make objects fly or levitate. Maybe you can use to make them away from the touch of the ground.\n"
            string+= "Three Words: {w18 iii 11 5    i 14 3 v v 15    9 ii 17 iii 15{n\n"
            string+= "You need to know how many vowels and consonants are their in the English Language.{n\n"
        elif self.args == " 3":
            string = "{cPuzzle(3){n\n"
            string+= "{gFreezing Charm{n - Immobilises living targets.\n"
            string+= "{wI M hvin 2 MOBILIS.{n\n"
            string+= "Get the Caps and ignore the rest.{n\n"
        elif self.args == " 4":
            string= "{gShield Charm{n - Creates a magical barrier to deflect physical entities and spell.{n\n"
            string+= "{w1-5-2\n"
            string+= "{wCON you do\n"
            string+= "{wEGO you rise\n"
            string+= "{wcare you yourself\n"
            string+= "{wlet you relax\n"
            string+= "{wso Tea you drink,\n"
            string+= "{wfollow my numbers\n"
            string+= "{wfollow the caps\n"
            string+= "{wand you get it right.{n\n"
            string+= "{gBoggart-Defense Charm{n - Remember Boggart takes the form of your worst fear and it may or may not be that powerful compared to what form it takes.\n"
            string+= "Harry knew what he feared the most was - A {rDementor.{n\n"
            string+= "{w|)\ | |) | ( |_| |_ |_| ^^{n\n"
            string+= "Haha! World is never too big. Just compress a bit and you will find everything.{n"
        else:
            string = "Please enter a valid serial number of the puzzle you want to remind yourself."
        self.caller.msg("%s"%string)

#------------------------------------------------------------------------------------------------------

class CmdDatabase(Command):
    key = "database"
    locks = "cmd:all()"
    auto_help = False

    def func(self):
        players = managers.players.all()
        scores = [player.db.score for player in players]
        respawns = [player.db.respawns for player in players]
        will = [player.db.will for player in players]
        for player in players:
            if not player.is_superuser:
                self.caller.msg("%s - %s %s %s\n" % (player,player.db.score,player.db.respawns,player.db.will))