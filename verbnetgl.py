"""
This file contains the classes for the form of Verbnet that have been enhanced
with GL event structures. The classes themselves do all the conversion necessary
given a VerbClass from verbnetparser.py
"""

from verbnetparser import VerbNetParser

class GLVerbClass(object):
    """VerbClass analogue, with an update mostly to frames"""
    
    def __init__(self, verbclass):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.roles = verbclass.themroles
        self.frames = self.frames()
        self.subclasses = [GLSubclass(sub, self.roles) for sub in verbclass.subclasses]
        
    def frames(self):
        return [GLFrame(frame, self.roles) for frame in self.verbclass.frames]

    def pp_html(self, fh):
        fh.write("<html>\n")
        fh.write("<head>\n")
        fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        fh.write("</head>\n")
        fh.write("<body>\n")
        fh.write("\n<h1>%s</h1>\n" % str(self.ID))
        for i in range(len(self.frames)):
            vn_frame = self.verbclass.frames[i]
            gl_frame = self.frames[i]
            fh.write("\n<table cellpadding=8 cellspacing=0 border=0 width=1000>\n")
            self.pp_html_description(gl_frame, fh)
            self.pp_html_example(gl_frame, fh)
            self.pp_html_predicate(vn_frame, fh)
            self.pp_html_subcat(gl_frame, fh)
            self.pp_html_qualia(gl_frame, fh)
            self.pp_html_event(gl_frame, fh)
            fh.write("</table>\n\n")

    def pp_html_description(self, gl_frame, fh):
        fh.write("<tr class=description>\n")
        fh.write("  <td colspan=2>%s\n" % ' '.join(gl_frame.pri_description))

    def pp_html_example(self, gl_frame, fh):
        fh.write("<tr class=vn valign=top>\n")
        fh.write("  <td width=180>Example\n")
        fh.write("  <td>\"%s\"" % gl_frame.example[0])

    def pp_html_predicate(self, vn_frame, fh):
        def predicate_str(pred):
            args = ', '.join([argtype[1] for argtype in pred.argtypes])
            return "<span class=pred>%s</span>(%s)" % (pred.value[0], args)
        fh.write("<tr class=vn valign=top>\n")
        fh.write("  <td width=180>VerbNet&nbsp;predicates\n")
        fh.write("  <td>")
        fh.write(', '.join([predicate_str(pred) for pred in vn_frame.predicates]))

    def pp_html_subcat(self, gl_frame, fh):
        fh.write("<tr class=qualia valign=top>\n")
        fh.write("  <td>GL&nbsp;subcategorisation\n")
        fh.write("  <td>\n")
        for element in gl_frame.subcat:
            #fh.write("      { %s } <br>\n" % element)
            fh.write("      {")
            if element.var is not None:
                fh.write(" var=%s" % element.var)
            fh.write(" cat=%s" % element.cat)
            if element.role:
                fh.write(" role=%s" % element.role[0])
            fh.write(" } / [")
            self.pp_html_restriction(element.sel_res, fh)
            fh.write("]<br>\n")

    def pp_html_restriction(self, restriction, fh):
        # print '>>', restriction
        if not restriction:
            pass
        elif restriction[0] in ['+', '-']:
            fh.write("%s%s" % (restriction[0], restriction[1]))
        elif restriction[0] in ['OR', 'AND'] and len(restriction) == 3:
            fh.write("(")
            self.pp_html_restriction(restriction[1], fh)
            fh.write(" %s " % restriction[0])
            self.pp_html_restriction(restriction[2], fh)
            fh.write(")")
        else:
            fh.write("%s" % restriction)

    def pp_html_qualia(self, gl_frame, fh):
        fh.write("<tr class=qualia valign=top>\n")
        fh.write("  <td>GL&nbsp;qualia&nbsp;structure\n")
        fh.write("  <td>%s\n" % gl_frame.qualia)

    def pp_html_event(self, gl_frame, fh):
        fh.write("<tr class=event valign=top>\n")
        fh.write("  <td>GL event structure")
        fh.write("  <td>var = %s<br>\n" % gl_frame.event_structure.var)
        fh.write("      initial_state = %s<br>\n" % gl_frame.event_structure.initial_state)
        fh.write("      final_state = %s\n" % gl_frame.event_structure.final_state)
            
    def __repr__(self):
        return str(self.ID) + " = {\n\nroles = " + str(self.roles) + \
               "\n\nframes = " + str(self.frames) + "\n}" + \
               "\n Subclasses = " + str(self.subclasses)


class GLSubclass(GLVerbClass):
    """Represents a subclass to a GLVerbClass. This needs to be different from
    GLVerbClass because VerbNet seems to change the THEMROLES section of the 
    subclass to only include thematic roles that differ from the main class,
    but does not list all the roles that stay the same. Since we need to update 
    self.roles, we can't call __init__ on the superclass because that would call
    self.frames and self.subclasses before we updated our roles properly.
    
    TODO: check this for proper nesting"""
    
    def __init__(self, verbclass, parent_roles):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.parent_roles = parent_roles
        self.subclass_only_roles = verbclass.themroles
        self.roles = self.themroles()
        self.frames = self.frames()
        self.subclasses = [GLSubclass(sub, self.roles) for sub in verbclass.subclasses]   
        
    def themroles(self):
        """Combines the thematic roles of the parent class and the current
        subclass. Replaces any version of the parent class's role with one from
        the subclass."""
        final_roles = self.subclass_only_roles
        for parent_role in self.parent_roles:
            duplicate = False
            for sub_role in self.subclass_only_roles:
                if parent_role.role_type == sub_role.role_type:
                    duplicate = True
            if not duplicate:
                final_roles.append(parent_role)
        return final_roles

class GLFrame(object):
    """GL enhanced VN frame that adds qualia and event structure, and links 
    syn/sem variables in the subcat to those in the event structure
    Event structure should be its own class or method?"""
    
    def __init__(self, frame, roles):
        self.vnframe = frame
        self.class_roles = roles
        self.pri_description = frame.primary
        self.sec_description = frame.secondary
        self.example = frame.examples
        self.subcat = self.subcat()
        self.qualia = None
        self.event_structure = None
        self.event_and_opposition_structure2()
        
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
            for themrole in self.class_roles:
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
            initial_state = State(mover_var, "?")
            final_state = State(mover_var, "-?")
            
        opposition = Opposition(None, initial_state, final_state)
        self.event_structure = EventStructure(initial_state, final_state)
        self.qualia = Qualia(self.vnframe.predicates[0], opposition)
        
    def event_and_opposition_structure2(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class
        """
        initial_states = []
        final_states = []        
        type_of_change = None
        
        # Get all the subcat members that have a variable
        member_vars = {}
        for submember in self.subcat:
            if submember.var not in [None, "e"]:
                member_vars[submember.role[0]] = submember.var
                
        # Get which ThemRole is changing because of the action, and its variable in the frame
        pred_type = None
        changers = []   # Can have more than one object with opposition
        unexpressed_changers = []
        start = []
        end = []
        for pred in self.vnframe.predicates:
            if pred.value[0] == 'motion' or pred.value[0] == 'transfer':
                pred_type = pred.value[0]
                for argtype, value in pred.argtypes:
                    if argtype == 'ThemRole':
                        changers.append(value)
                        unexpressed_changers.append('?' + value)
                    
        if pred_type and 'exchange' not in self.vnframe.class_ID and 'butter' not in self.vnframe.class_ID:
            equals = []
            for pred in self.vnframe.predicates:
                if pred.value[0] == 'path_rel':
                    is_start = False
                    is_end = False
                    local_changer = None
                    opposition = None       # where the object is or who owns it
                    for argtype, value in pred.argtypes:
                        if value in changers or value in unexpressed_changers:
                            local_changer = value
                        if argtype == 'ThemRole' and value not in changers and \
                        value not in unexpressed_changers:
                            opposition = value
                        if value == 'end(E)':
                            is_end = True
                        if value == 'start(E)':
                            is_start = True
                        if value == 'ch_of_poss' or value == 'ch_of_pos':
                            type_of_change = "pos"
                        if value == 'ch_of_loc' or value == 'ch_of_location':
                            type_of_change = "loc"
                        if value == 'ch_of_info':
                            type_of_change = "info"
                        if value == 'ch_of_state':
                            type_of_change = "state"
                    if is_start:
                        start.append(tuple((local_changer, opposition)))
                    if is_end:
                        end.append(tuple((local_changer, opposition)))
                if pred.value[0] == 'equals':
                    equals.append(tuple(value for argtype, value in pred.argtypes))
            
            if type_of_change != 'info':
                for changer, opposition in start:
                    final_opp = opposition
                    if len(equals) > 0:
                        for pair in equals:
                            if pair[0] == opposition:
                                final_opp = pair[1]
                            elif pair[1] == opposition:
                                final_opp = pair[0]
                    print changer, final_opp, self.vnframe.class_ID
                    try:
                        changer_var = member_vars[changer]
                    except KeyError:
                        changer_var = changer
                    try: 
                        opp_var = member_vars[final_opp]
                    except KeyError:
                        opp_var = final_opp
                    initial_states.append(State(changer_var, opp_var))
                for changer, opposition in end:
                    final_opp = opposition
                    if len(equals) > 0:
                        for pair in equals:
                            if pair[0] == opposition:
                                final_opp = pair[1]
                            elif pair[1] == opposition:
                                final_opp = pair[0]
                    print changer, final_opp, self.vnframe.class_ID
                    try:
                        changer_var = member_vars[changer]
                    except KeyError:
                        changer_var = changer
                    try: 
                        opp_var = member_vars[final_opp]
                    except KeyError:
                        opp_var = final_opp
                    final_states.append(State(changer_var, opp_var))
            
        opposition = Opposition(type_of_change, initial_states, final_states)
        self.event_structure = EventStructure(initial_states, final_states)
        self.qualia = Qualia(pred_type, opposition)
    
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
    location. For transfer verbs, this gives the variable assignment of the 
    object being transferred, and what currently owns the object"""
    
    def __init__(self, obj_var, pos_var):
        self.object_var = obj_var
        self.position = pos_var
        
    def __repr__(self):
        return "{ objects." + str(self.object_var) + ".location = " + \
                str(self.position) + " }"


class EventStructure(object):
    """Defines the event structure for a particular frame of a verb"""
    
    def __init__(self, initial_states, final_states):
        self.var = "e"
        self.states = "To Be Determined"
        self.initial_states = initial_states
        self.final_states = final_states
        self.program = "To Be Determined"
     
    def __repr__(self):
        output = "\n\tvar = " + str(self.var) + "\n\tinitial_state = " + \
                 str(self.initial_states) + "\n\tfinal_ state = " + \
                 str(self.final_states) + "\n\tprogram = " + str(self.program)
        return output


class Opposition(object):
    """Represents the opposition structure of the frame
    Right now only tailored for locations"""
    
    def __init__(self, type_of_change, initial_states, final_states):
        self.type_of_change = type_of_change
        self.initial_states = initial_states
        self.final_states = final_states
        
    def __repr__(self):
        return str(self.initial_states) + str(self.final_states)
        
        #if self.initial_state.position:
        #    return "(At(" + str(self.initial_state.object_var) + ", " + \
        #               str(self.initial_state.position) + "), At(" + \
        #               str(self.final_state.object_var) + ", " + \
        #               str(self.final_state.position) + ")) "
        #else:
        #    return "(At(" + str(self.initial_state.object_var) + ", ?), At(" + \
        #               str(self.final_state.object_var) + ", -?)) "

    
class Qualia(object):
    """Represents the qualia structure of a verbframe, including opposition
    structure"""
    
    def __init__(self, pred_type, opposition):
        self.formal = pred_type
        self.opposition = opposition
        
    def __repr__(self):
        return "{ formal = " + str(self.formal) + "(e) AND Opposition" + \
               str(self.opposition) + "}"

def search2(verbclasslist, pred_type=None, themroles=None, synroles=None, semroles=None):
    """Returns verbclasses that match search parameters
    TODO: figure out what it means to search for themroles, synroles, and semroles"""
    successes = []
    for vc in verbclasslist:
        for frame in vc.frames:
            for pred in frame.vnframe.predicates:
                if pred.value[0] == pred_type:
                    if vc not in successes:
                        successes.append(vc)
    return successes


def pp_html(results):
    INDEX = open('html/index.html', 'w')
    INDEX.write("<html>\n")
    INDEX.write("<head>\n")
    INDEX.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
    INDEX.write("</head>\n")
    INDEX.write("<body>\n")
    INDEX.write("<table cellpadding=8 cellspacing=0>\n")
    INDEX.write("<tr class=header><td>VN Motion Classes</a>\n")
    for result in results:
        class_file = "vnclass-%s.html" % result.ID
        INDEX.write("<tr class=vnlink><td><a href=\"%s\">%s</a>\n" % (class_file, result.ID))
        VNCLASS =  open("html/%s" % class_file, 'w')
        result.pp_html(VNCLASS)
    INDEX.write("</table>\n")
    INDEX.write("</body>\n")
    INDEX.write("</html>\n")


if __name__ == '__main__':
    
    vnp = VerbNetParser()
    vngl = [GLVerbClass(vc) for vc in vnp.verb_classes]
    results = search2(vngl, "motion")
    print len(results)
    print vngl[269] #slide
    #pp_html(results)
    possession_results = search2(vngl, "has_possession")
    print len(possession_results)
    for vc in possession_results:
        print vc.ID
    #for vc in vngl:
    #    if vc.ID == "give-13.1":
    #        print vc
    # find all 'ch_of_' predicate argument types
    results2 = []
    for vc in vngl:
        for frame in vc.frames:
            for pred in frame.vnframe.predicates:
                for arg, arg_type in pred.argtypes:
                    if 'ch_of_' in arg_type:
                        if arg_type not in results2:
                            results2.append(arg_type)
    print results2
    # find all "ch_of_info" verb classes
    results3 = []
    for vc in vngl:
        for frame in vc.frames:
            for pred in frame.vnframe.predicates:
                for arg, arg_type in pred.argtypes:
                    if 'ch_of_info' in arg_type:
                        if vc.ID not in results3:
                            results3.append(vc.ID)
    print results3