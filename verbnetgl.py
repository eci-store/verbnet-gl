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
        self.qualia = self.qualia()
        self.event_structure = EventStructure(self.subcat, vnclass.themroles, frame.predicates)
        
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
    
    def qualia(self):
        """Creates the qualia structure that shows opposition if needed"""
        pass
    
    def __repr__(self):
        output = "\n{ description = " + str(" ".join(self.pri_description)) + \
        "\nexample = " + str(self.example[0]) + "\nsubcat = " + str(self.subcat)
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
        output = "{ var = " + str(self.var) + ", cat = " + str(self.cat) + \
                 ", role = " + str(self.role) + " } / " + str(self.sel_res) + "\n"
        return output

class EventStructure(object):
    """Defines the event structure for a particular frame of a verb"""
    
    def __init__(self, subcat, themroles, pred):
        self.subcat = subcat
        self.themroles = themroles
        self.pred = pred
        self.var = "e"
        self.states = "To Be Determined"
        self.initial_state = self.states[0]
        self.final_states = self.states[1]
        self.program = "To Be Determined"
        
    def states(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class
        
        TODO: Use the themroles and subcat to determine if locations need to be 
        marked with a ? - whether all themroles appear in syntax or not
        
        Use path_rel and subcat to determine if initial_state and final_state
        are the same variable
        """
        pass
    
# Test it out
if __name__ == '__main__':
    
    vnp = VerbNetParser()
    print len(vnp.parsed_files)
    vngl = [GLVerbClass(vc) for vc in vnp.verb_classes]
    print len(vngl)
    print vngl[269]