"""
This file contains the classes for the form of Verbnet that have been enhanced
with GL event structures. The classes themselves do all the conversion necessary
given a VerbClass from verbnetparser.py
"""

import verbnetparser

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
        return [GLFrame(frame, self.verbclass) for frame in self.verbclass.frames)
            
    def __repr__(self):
        return str(self.ID) + str(self.frames)
        
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
        #self.event_structure = EventStructure(self.somekindainfo)
        
    def subcat(self):
        """Creates the subcat frame structure with unique variables assigned to
        different phrases/roles"""
        pass
    
    def qualia(self):
        """Creates the qualia structure that shows opposition if needed"""
        pass
        
        
class EventStructure(object):
    """Defines the event structure for a particular frame of a verb"""
    
    def __init__(self, var, pred):
        self.var = var
        self.states = "list of states?"
        self.initial_state = self.states[0]
        self.final_states = self.states[1]
        self.program = "Related to name of verb in frame/a list of programs?"
        
    def states(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class
        Use self.var somehow"""
        pass