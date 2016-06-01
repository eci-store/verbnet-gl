"""
This file contains the classes for the form of Verbnet that have been enhanced
with GL event structures. The classes themselves do all the conversion necessary
given a VerbClass from verbnetparser.py
"""

from verbnetparser import *

class GLVerbClass(object):
    """VerbClass analogue, with an update mostly to frames"""
    
    def __init__(self, verbclass):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.roles = verbclass.themroles
        self.frames = self.frames()
        
    def frames(self):
        return [GLFrame(frame, self.verbclass) for frame in self.verbclass.frames]
            
    def __repr__(self):
        return str(self.ID) + " = {\n\nroles = " + str(self.roles) + \
               "\n\nframes = " + str(self.frames) + "\n}"
        
class GLFrame(object):
    """GL enhanced VN frame that adds qualia and event structure, and links 
    syn/sem variables in the subcat to those in the event structure
    Event structure should be its own class or method?"""
    
    def __init__(self, frame, vnclass):
        self.vnframe = frame
        self.vnclass = vnclass
        self.pri_description = frame.primary
        self.sec_description = frame.secondary
        self.example = frame.examples
        self.subcat = self.subcat()
        self.qualia = None
        self.event_structure = None
        self.event_and_opposition_structure()
        
    def subcat(self):
        """Creates the subcat frame structure with unique variables assigned to
        different phrases/roles"""
        i = 0
        members = []
        for synrole in self.vnframe.syntax:
            if synrole.POS in ["ADV", "PREP", "ADJ"]:
                members.append(SubcatMember(None, synrole, None))
                continue
            elif synrole.POS == "VERB":
                members.append(SubcatMember("e", synrole, None))
                continue
            added = False
            for themrole in self.vnclass.themroles:
                if str(synrole.value[0]).lower() == str(themrole.role_type).lower():
                    if str(synrole.POS) == "NP":
                        members.append(SubcatMember(i, synrole, themrole))
                        i += 1
                        added = True
                    else:
                        members.append(SubcatMember(None, synrole, themrole))
                        added = True
            if not added:
                members.append(SubcatMember(None, synrole, None))
        return members
    
    def event_and_opposition_structure(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class
        
        TODO: Figure out if path_rel is really necessary. It has start/end, 
        specifies which ThemRole is undergoing the event (Theme/Agent), and 
        whether it is Initial_Location/Destination. But the "motion" predicate
        seems to tell you which ThemRole is undergoing the movement, so what 
        more does path_rel get us?
        
        This is a target for generalization. Right now it only works with motion
        predicates. Ideally you want to compare all of the frame's subcat members
        to all of the class's thematic roles to see what is missing, and then 
        assign ?'s accordingly.
        """
        initial_state = None
        final_state = None
        # Get all the subcat members that have a variable
        members_to_assign = []
        for submember in self.subcat:
            if submember.var not in [None, "e"]:
                members_to_assign.append(submember)
                
        # Get which ThemRole is moving, and its variable in the frame
        mover = None 
        mover_var = None
        initial_loc = None
        destination = None
        for pred in self.vnframe.predicates:
            if pred.value[0] == 'motion':
                for argtype, value in pred.argtypes:
                    if argtype == 'ThemRole':
                        mover = value
        if mover:
            for member in members_to_assign:
                if member.role[0] == mover:
                    mover_var = member.var
                if member.role[0] == "Initial_Location":
                    initial_loc = member.var
                if member.role[0] == "Destination":
                    destination = member.var
                    
        # Instantiate the two states            
        if initial_loc:
            initial_state = State(mover_var, initial_loc)
            if destination:
                final_state = State(mover_var, destination)
            else:
                final_state = State(mover_var, -initial_loc)
        elif destination:
            initial_state = State(mover_var, -destination)
            final_state = State(mover_var, destination)
        else:
            initial_state = State(mover_var, None)
            final_state = State(mover_var, None)
            
        opposition = Opposition(initial_state, final_state)
        self.event_structure = EventStructure(initial_state, final_state)
        self.qualia = Qualia(self.vnframe.predicates[0], opposition)
    
    def __repr__(self):
        output = "\n\n{ description = " + str(" ".join(self.pri_description)) + \
                 "\nexample = " + str(self.example[0]) + \
                 "\nsubcat = " + str(self.subcat) + \
                 "\nqualia = " + str(self.qualia) + \
                 "\nevent_structure = {" + str(self.event_structure) + "\t}\n"
        return output

class SubcatMember(object):
    """A combination of SyntacticRole and ThematicRole"""
    
    def __init__(self, var, synrole, themrole):
        self.var = var
        self.cat = synrole.POS
        self.role = synrole.value   #themrole.role_type won't work
        if themrole is not None:
            self.sel_res = themrole.sel_restrictions
        else:
            self.sel_res = synrole.restrictions

    def __repr__(self):
        output = "\n\t{ var = " + str(self.var) + \
                 ", cat = " + str(self.cat) + \
                 ", role = " + str(self.role) + \
                 " } / " + str(self.sel_res)
        return output
      
class State(object):
    """Represents a state in the event structure
    For motion verbs, this gives the variable assignment of the mover, and its
    location"""
    
    def __init__(self, obj_var, loc_var):
        self.object_var = obj_var
        self.location = loc_var
        
    def __repr__(self):
        loc = self.location
        if not loc:
            loc = "?"
        return "{ objects." + str(self.object_var) + ".location = " + str(loc) + " }"

class EventStructure(object):
    """Defines the event structure for a particular frame of a verb"""
    
    def __init__(self, initial_state, final_state):
        self.var = "e"
        self.states = "To Be Determined"
        self.initial_state = initial_state
        self.final_state = final_state
        self.program = "To Be Determined"
     
    def __repr__(self):
        output = "\n\tvar = " + str(self.var) + "\n\tinitial_state = " + \
                 str(self.initial_state) + "\n\tfinal_ state = " + \
                 str(self.final_state) + "\n\tprogram = " + str(self.program)
        return output

class Opposition(object):
    """Represents the opposition structure of the frame
    Right now only tailored for locations"""
    
    def __init__(self, initial_state, final_state):
        self.initial_state = initial_state
        self.final_state = final_state
        
    def __repr__(self):
        if self.initial_state.location:
            return "(At(" + str(self.initial_state.object_var) + ", " + \
                       str(self.initial_state.location) + "), At(" + \
                       str(self.final_state.object_var) + ", " + \
                       str(self.final_state.location) + ") "
        else:
            return ""
    
class Qualia(object):
    """Represents the qualia structure of a verbframe, including opposition
    structure"""
    
    def __init__(self, predicate, opposition):
        self.formal = predicate.value
        self.opposition = opposition
        
    def __repr__(self):
        return "{ formal = " + str(self.formal) + "(e) AND Opposition " + \
               str(self.opposition) + "}"
        
# Test it out
if __name__ == '__main__':
    
    vnp = VerbNetParser()
    print len(vnp.parsed_files)
    vngl = [GLVerbClass(vc) for vc in vnp.verb_classes]
    print len(vngl)
    print vngl[269]