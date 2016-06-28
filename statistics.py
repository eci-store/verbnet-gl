"""Calculates stastistics about information related to verbnet, including types
of predicates.
Likely lots of redundancy"""

from verbnetgl import *
from collections import Counter

class PredicateStatistics(object):
    
    def __init__(self, glvc):
        self.glverbclasses = glvc
        self.predicates = Counter()
        self.argtypes = Counter()
        self.themroles = Counter()
        self.synroles = Counter()
        self.POS = Counter()
        self.collect_predicates()
        self.collect_themroles()
        self.collect_syntax()
        self.motion_check = self.check_classes("motion")
        self.cause_check = self.check_classes("cause")
        self.pathrel_check = self.check_classes("path_rel")
        self.transfer_check = self.check_classes("transfer")
        
    def collect_predicates(self):
        """Gather the count of all predicates in the list of GLVerbClasses"""
        for vc in self.glverbclasses:
            for frame in vc.frames:
                for pred in frame.vnframe.predicates:
                    self.predicates[pred.value[0]] += 1
            for subclass in vc.subclasses:
                sub_preds = self.recursive_collect(subclass)
                self.predicates.update(sub_preds)
                
    def recursive_collect(self, subclass):
        predicates = Counter()
        if len(subclass.subclasses) == 0:
            for frame in subclass.frames:
                for pred in frame.vnframe.predicates:
                    self.predicates[pred.value[0]] += 1
            return predicates
        else:
            for subc in subclass.subclasses:
                predicates.update(self.recursive_collect(subc))
            return predicates

    def collect_themroles(self):
        """Gather the count of all thematic roles in the list of GLVerbClasses
        TODO: subclasses"""
        for vc in self.glverbclasses:
            for role in vc.roles:
                self.themroles[role.role_type] += 1
    
    def collect_syntax(self):
        """Gather the count of all syntactic roles/POS in the list of GLVerbClasses
        TODO: subclasses"""
        for vc in self.glverbclasses:
            for frame in vc.frames:
                for synrole in frame.vnframe.syntax:
                    self.POS[synrole.POS] += 1
                    if len(synrole.value) > 0:
                        self.synroles[synrole.value[0]] += 1
    
    def check_classes(self, target_pred):
        """Checks to see if all predicate types (e.g. motion) of a class have
        the same value
        TODO: include subclasses"""
        differing_classes = set()
        for vc in self.glverbclasses:
            contains_pred = True
            for i in range(len(vc.frames)):
                preds = vc.frames[i].vnframe.predicates
                single_frame_contains_pred = False
                for pred in preds:
                    if pred.value[0] == target_pred:
                        single_frame_contains_pred = True
                if i == 0:
                    if not single_frame_contains_pred:
                        contains_pred = False
                else:
                    if contains_pred != single_frame_contains_pred:
                        differing_classes.add(vc.ID)
        return sorted(list(differing_classes))
        
    def pred_search_by_frame(self, verbclasslist, pred_type):
        """Returns frames that match search parameters
        TODO: include subclasses"""
        successes = set()
        for vc in verbclasslist:
            for i in range(len(vc.frames)):
                for pred in vc.frames[i].vnframe.predicates:
                    if pred.value[0] == pred_type:
                        successes.add(str(vc.ID) + "--" + str(i+1))
        return sorted(list(successes))
                    

# Get the goods
if __name__ == '__main__':
    vnp = VerbNetParser()
    vngl = [GLVerbClass(vc) for vc in vnp.verb_classes]
    print "Total Number of classes: ", len(vngl)
    stats = PredicateStatistics(vngl)
    print "\nPredicates: ", stats.predicates
    print "\nThematic Roles: ", stats.themroles
    print "\nSyntactic Roles: ", stats.synroles
    print "\nPOS: ", stats.POS
    print "\nTotal number of predicates: ", sum(stats.predicates.values())
    print "\nClasses without all frames containing motion: ", stats.motion_check
    print "\nClasses without all frames containing cause: ", stats.cause_check
    print "\nClasses without all frames containing path_rel: ", stats.pathrel_check
    print "\nClasses without all frames containing transfer: ", stats.transfer_check
    motion_classes = [vc.ID for vc in search2(vngl, "motion")]
    print "\nAll motion classes: ", motion_classes
    print "\nNumber of motion classes: ", len(motion_classes)
    motion_frames = stats.pred_search_by_frame(vngl, "motion")
    print "\nAll motion frames: ", motion_frames
    print "\nNumber of motion frames: ", len(motion_frames)
    transfer_classes = [vc.ID for vc in search2(vngl, "transfer")]
    print "\nAll transfer classes: ", transfer_classes
    print "\nNumber of transfer classes: ", len(transfer_classes)
    transfer_frames = stats.pred_search_by_frame(vngl, "transfer")
    print "\nAll transfer frames: ", transfer_frames
    print "\nNumber of transfer frames: ", len(transfer_frames)