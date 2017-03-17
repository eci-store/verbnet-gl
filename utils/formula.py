"""formula.py

Simple implementation for formulas.

"""


class Formula(object):

    """Simple implementation for formulas. A formula is (1) a predicate like
    motion(e), (2) a variable like x or x1, or (3) a negation of a formula."""

    def __ne__(self, other):
        return self.__eq__(other)


class Pred(Formula):

    """To implement things like motion(e) and At(x,y), but also more complex
    things like holds(t1,At(x,y))."""

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
        return "%s(%s)" % (self.pred, ', '.join([f.html() for f in self.formulas]))


class At(Pred):

    def __init__(self, object_var, location_var):
        # This is just like a regular Pred, but store indivudual elements in
        # special variables for easy access
        self.pred = 'At'
        self.formulas = [object_var, location_var]
        self.obj = self.formulas[0]
        self.location = self.formulas[1]

    def set_location(self, new_location):
        # Updating the location must be done for both places where it is defined
        self.formulas[1] = new_location
        self.location = new_location


class Has(Pred):

    def __init__(self, owner_var, object_var, ):
        # This is just like a regular Pred, but store indivudual elements in
        # special variables for easy access
        self.pred = 'Has'
        self.formulas = [owner_var, object_var]
        # TODO: instead of the following, maybe use something like
        # self.slots = { 'time': 0, 'object': 1, 'owner': 2 }
        self.owner = self.formulas[0]
        self.obj = self.formulas[1]

    def set_owner(self, new_owner):
        # Updating the owner must be done for both places where it is defined
        # TODO: this could be done through the slots
        self.formulas[0] = new_owner
        self.owner = new_owner


class Holds(Pred):

    def __init__(self, time_var, formula):
        self.pred = 'Holds'
        self.formulas = [time_var, formula]
        self.time = time_var
        self.formula = formula


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

    """Implements a variable, mostly so we can print it nicely. Variables can
    be a single letter like 'x' or a letter with an integer like 'x1' or the
    anonomous variable '?'."""

    def __init__(self, variable):
        self.ID = variable

    def __str__(self):
        return self.ID

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.ID == other.ID

    def html(self):
        if len(self.ID) == 1:
            return self.ID
        else:
            return "%s<sub>%s</sub>" % (self.ID[0], self.ID[1:])
