"""deprecated.py

This has the old code that introduces oppositions, which used to be in the class
verbnetgl.GLFrame. After refactoring I still did not understand it and it seemed
to be doing the wrong thing anyway. Kept around for reference for now since it
does seem to have useful ideas.

"""

    def event_and_opposition_structure2(self):
        """Uses the frame information to determine what initial and final states
        should look like, given the variables available in the subcat frame, and
        the roles for the verb class."""

        # TODO: after some refactoring this method is still way too hard to
        # understand and it must be completely changed

        states = []
        type_of_change = None
        member_vars = self._get_variables()  # all subcat members that have a variable
        start = []
        end = []
        pred_type = self._find_opposition_predicate()
        #self._debug0(member_vars, pred_type)

        if pred_type:
            equals = []
            changers = []

            for pred in self.vnframe.predicates:
                if pred.value[0] == 'path_rel': 
                    changer, opposition = self._set_changer_and_opposition(pred, member_vars)
                    type_of_change = self._set_type_of_change(pred)
                    self._update_start_and_end(pred, changer, opposition, start, end)
                if pred.value[0] == 'equals':
                    equals.append(tuple(value for argtype, value in pred.argtypes))
            #self._debug1(equals, start, end, member_vars, pred_type)

            # Go through all objects that change state, and if beginning and end
            # are expressed syntactically, create the opposition. (HUH: if I try
            # to make this one method _add_oppositions_to_states then it chokes
            # on changer not being available, it is fine with the code below
            # though)
            for changer_s, opposition_s in start:
                start_opp = self._get_start_opp(equals, opposition_s)
                self._add_opposition_to_states(end, changers, changer, changer_s,
                                               equals, member_vars, start_opp, states)

            # Check for objects that only appear syntactically as an end        
            for changer, opposition in end:
                self._add_opposition_to_states2(changers, changer, opposition, equals, member_vars, states)

            # No path_rel predicates
            if len(changers) == 0:
                changer = '?'
                for pred in self.vnframe.predicates:
                    if pred.value[0] == pred_type:
                        changer = pred.argtypes[1][1]
                changer_var = member_vars.get(changer, changer)
                start_state = State(changer_var, '?')
                final_state = State(changer_var, '-?')
                states.append(tuple((start_state, final_state)))
                    
        opposition = Opposition(type_of_change, states)
        print self
        self.events = EventStructure(states)
        self.qualia = Qualia(pred_type, opposition)


    def _find_opposition_predicate(self):
        """Check whether one of the predicates in the frame is deemed intersting for
        oppositions.  Returns None if there is no such predicate and returns the
        predicate value of the last one of those predicates if there is one."""
        pred_type = None
        for pred in self.vnframe.predicates:
            #print '  ', pred
            if pred.value[0] in ['motion', 'transfer', 'cause', 'transfer_info', \
                'adjust', 'emotional_state', 'location', 'state', 'wear']:
                pred_type = pred.value[0]
        return pred_type

    def _set_type_of_change(self, pred):
        """Check the argument types of the predicate for certain change predicates, if
        there is one then return 'pos', 'loc', 'info' or 'state', else return None."""
        # TODO: this relies on there being at least 4 argtypes in the predicate,
        # is that kosher?
        type_of_change = None
        if pred.argtypes[3][1] == 'ch_of_poss' or pred.argtypes[3][1] == 'ch_of_pos':
            type_of_change = "pos"
        if pred.argtypes[3][1] == 'ch_of_loc' or pred.argtypes[3][1] == 'ch_of_location':
            type_of_change = "loc"
        if pred.argtypes[3][1] == 'ch_of_info':
            type_of_change = "info"
        if pred.argtypes[3][1] == 'ch_of_state':
            type_of_change = "state"
        return type_of_change

    def _set_changer_and_opposition(self, pred, member_vars):
        """Check to see where the object that changes is, and where that object
        is or who owns it."""
        # TODO: find out why this works
        # NOTE: it does not seem to do the right thing on first glance
        if pred.argtypes[1][1] in member_vars.keys():
            changer = pred.argtypes[1][1]       # object that changes
            opposition = pred.argtypes[2][1]    # where the object is or who owns it
        else:
            changer = pred.argtypes[2][1]       # object that changes
            opposition = pred.argtypes[1][1]
        return changer, opposition

    def _update_start_and_end(self, pred, changer, opposition, start, end):
        """Add (changer, opposition) pair to start and/or end if predicate includes
        start(E) or end(E) argtype."""
        if pred.argtypes[0][1] == 'start(E)':
            start.append(tuple((changer, opposition)))
        if pred.argtypes[0][1] == 'end(E)':
            end.append(tuple((changer, opposition)))

    def _get_start_opp(self, equals, opposition_s):
        start_opp = opposition_s
        if len(equals) > 0:
            for pair in equals:
                if pair[1] == opposition_s:
                    start_opp = pair[0]
        return start_opp

    def _get_end_opp(self, equals, opposition_e):
        end_opp = opposition_e
        if len(equals) > 0:
            for pair in equals:
                if pair[1] == opposition_e:
                    end_opp = pair[0]
        return end_opp

    def _add_opposition_to_states(self, end, changers, changer, changer_s, equals,
                                  member_vars, start_opp, states):
        """Adds opposition to states for those cases where both the initial and the
        final state are expressed."""
        changer_s_var = member_vars.get(changer_s, changer_s)
        opp_s_var = member_vars.get(start_opp, '?')
        is_end = False
        for changer_e, opposition_e in end:
            if changer_s == changer_e:
                is_end = True
                changers.append(changer_s)
                end_opp = self._get_end_opp(equals, opposition_e)
                opp_e_var = member_vars.get(end_opp, '?')
                start_state = State(changer_s_var, opp_s_var)
                final_state = State(changer_s_var, opp_e_var)
                states.append(tuple((start_state, final_state)))
        if not is_end:
            changers.append(changer)
            start_state = State(changer_s_var, opp_s_var)
            final_state = State(changer_s_var, "-" + str(opp_s_var))
            states.append(tuple((start_state, final_state)))

    def _add_opposition_to_states2(self, changers, changer, opposition,
                                   equals, member_vars, states):
        """Adds opposition to states for those cases where only the final state is
        expressed."""
        if changer not in changers:
            changers.append(changer)
            end_opp = opposition
            if len(equals) > 0:
                for pair in equals:
                    if pair[1] == opposition:
                        end_opp = pair[0]
            changer_var = member_vars.get(changer, changer)
            opp_var = member_vars.get(end_opp, '?')
            start_state = State(changer_var, "-" + str(opp_var))
            final_state = State(changer_var, opp_var)
            states.append(tuple((start_state, final_state)))

    def _debug0(self, member_vars, pred_type):
        print "\n", self.glverbclass.ID, ' '.join(self.pri_description)
        print '  ', member_vars
        print '   pred_type =', pred_type

    def _debug1(self, equals, start, end, member_vars, pred_type):
        if equals or start or end:
            print "\n", self.glverbclass.ID, ' '.join(self.pri_description)
            print "   member_vars = %s" % member_vars 
            print "   pred_type   = %s" % pred_type
            print "   equals      = %s" % equals
            print "   start       = [%s]" % ', '.join(["%s-%s" % (x, y) for x, y in start])
            print "   end         = [%s]" % ', '.join(["%s-%s" % (x, y) for x, y in end])
