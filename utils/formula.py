"""formula.py

Simple implementation for formulas.

"""


class Formula(object):

    """Simple implementation for formulas. A formula is (1) a predicate like
    motion(e), (2) a variable like x or x1, or (3) a negation of a predicate."""

    def __ne__(self, other):
        return self.__eq__(other)


class Pred(Formula):

    """To implement things like motion(e) and At(x1,x2), but also more complex
    things like holds(te,At(x1,x2))."""

    def __init__(self, pred, formulas):
        self.pred = pred
        self.formulas = formulas

    def __str__(self):
        return "%s(%s)" % (self.pred, ', '.join([str(f) for f in self.formulas]))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self.pred == other.pred) and (self.formulas == other.formulas)

    def html(self):
        return "<span class=pred>%s</span>(%s)" \
            % (self.pred.lower(), ', '.join([f.html() for f in self.formulas]))


class At(Pred):
    def __init__(self, object_var, location_var):
        Pred.__init__(self, 'At', [object_var, location_var])


class Have(Pred):
    def __init__(self, owner_var, object_var, ):
        Pred.__init__(self, 'Have', [owner_var, object_var])


class Holds(Pred):
    def __init__(self, time_var, formula):
        Pred.__init__(self, 'Holds-in', [time_var, formula])


class Not(Formula):

    def __init__(self, formula):
        self.formula = formula

    def __str__(self):
        return "-%s" % self.formula

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.formula == other.formula

    def html(self):
        return "&not;%s" % self.formula.html()


class Var(Formula):

    """Implements a variable, mostly so we can print it nicely. Variables can be
    a string like 'Traj' or a letter with an integer like 'x1'. Also keeps track
    of counts for variables that are not used in the subcategorisation."""

    variable_count = 0

    @classmethod
    def get_unbound_variable(cls):
        Var.variable_count += 1
        return "x%d" % Var.variable_count

    @classmethod
    def reset_unbound_variable_count(cls):
        Var.variable_count = 0

    def __init__(self, variable):
        self.ID = variable

    def __str__(self):
        return self.ID

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.ID == other.ID

    def html(self):
        if self.ID[0] == 'x':
            return "<i>%s<sub>%s</sub></i>" % (self.ID[0], self.ID[1:])
        else:
            return "<i>%s</i>" % self.ID
