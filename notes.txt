The goal of this project is to automatically add GL event structure to VerbNet verbs (to the extent it is possible). Starting with the verb slide, then generalizing to all verbs of motion, and then ideally to all other types of verbs in VerbNet. 

http://verbs.colorado.edu/~mpalmer/projects/verbnet.html

For guidelines on VerbNet go here: http://verbs.colorado.edu/verb-index/VerbNet_Guidelines.pdf

Right now the goal is to get entries with structure that looks like this:

slide-11.2 = {

   roles = [ Agent / +int_control,
	     Theme / +concrete,
	     Initial_Location / +location,
	     Final_Location / (+animate ∨ (+location ∧ -region)),
	     Intermediate_Location ]

   frames = [

      { description = "NP V",
  	example = "The books slid.",
  	subcat = [ { var = x, cat = NP, role = Theme } / +concrete,
             	   { var = e, cat = VERB } ],
  	qualia = { formal = Motion(e) },
  	event_structure = { 
     		var = e,
     		initial_state = { objects.x.location = ?loc1 },
     		final_state = { objects.x.location = ?loc2 },
     		program = SLIDE(e, x, ?y, env) } }
   ]
}

The code currently consists of two programs: verbnetparser.py and verbnetgl.py, as well as all the xml files for VerbNet version 3.2.4 (analyze.py and verbnet.py are initial programs by Marc Verhagen for experimentation). 


verbnetparser.py is a program to read in VerbNet XML files and convert them into Python objects that can be easily manipulated. The class structure is therefore similar to VerbNet entries. BeautifulSoup is used to work with the xml code.

Classes
-------

VerbNetParser is used to parse a whole directory of VerbNet xml files and convert all of them into a list VerbClass objects. 

Ex.
vnp = VerbNetParser()
vc1 = vnp.verb_classes[269]


AbstractXML is a superclass used by all other classes that have to deal with XML code, and has the sole method get_category() that allows for easy extraction of BeautifulSoup object categories.


VerbClass represents an entire verb class in VerbNet, with a class ID, list of verb Members in the class with their numbered links to FrameNet/WordNet/Xtag, a list of frames, a list of verb members by name only (no link markers), and all the thematic roles for the class.

Ex.
print vc1.names
print vc1.frames
print vc1.themroles


Member represents a single member of a verb class, with its name, wn (wordnet category), and grouping.


Frame represents a single frame of a VerbClass, with a VerbNet description number, a list of primary and secondary syntactic elements, an xtag, example sentences, a syntactic subcategorization (a list of SyntacticRoles), and a list of semantic Predicates.


ThematicRole represents a single thematic role, which appears in the VerbClass, which may or may not be realized in a particular Frame as a SyntacticRole. Contains a role (Agent, Theme, etc.) and any selectional restrictions.


Predicates represent the semantic predicates that are assigned to a Frame. It has a value (i.e. motion), a list of all arguments in the predicate, and then a list of (type, value) tuples for every argument.


SyntacticRole represents a single role in the Frame's subcategorization. It has a POS, semantic value (Agent, Theme, etc.) which should line up with one of the ThematicRoles of the VerbClass, and a list of selectional restrictions.


There is a search function which takes in a list of verbclasses, and a predicate type (e.g. motion) and returns a list of all frames that contain that predicate type. More functionality is planned for this search, if it seems useful in the future.

Ex. 
results = search(vnp.verb_classes, "motion")



------------------------------------------
verbnetgl.py is a program to automatically add GL event structure to VerbNet classes. It creates classes that use the classes created in verbnetparser.py instead of dealing with xml directly.

Classes
-------

GLVerbClass is the analogue to VerbClass. 

GLFrame is the analogue to Frame, with added qualia and event_structure. The subcat list differs in that each SubcatMember is a combination of a SyntacticRole and ThematicRole - each member that has a thematic role (Agent, Theme, etc.) is given a unique variable, so that the opposition and event structures can take advantage of this.

SubcatMember has POS, role (Agent, etc.), and selectional restrictions combined from the SyntacticRole and ThematicRole. 

EventStructure represents the event structure, based around the example above, with a variable, initial_state, final_state, and program. What we will do with programs is still TBD.

State represents the initial or final state in the event structure. For motion verbs, the object_var represents the unique variable assigned to the SubcatMember which is moving in the event, and location is the unique variable assigned to the SubcatMember associated to either Initial_Location or Destination. Location can be None if there is neither an initial location or destination available in the Subcat for the frame. If initial location is given in the Subcat but no destination, then the final_state will take the negation of the value for the initial location (i.e. the value for the location of the final_state is /not/ the location of the initial location).

Opposition represents the opposition structure of a GLFrame, as part of the Qualia structure. Currently only used for printing, but will likely expand once oppositions for things other than locations are needed.

Qualia represents the qualia structure of the GLFrame, with format and opposition structure.


Ex.
vnp = VerbNetParser()
vngl = [GLVerbClass(vc) for vc in vnp.verb_classes]
print vngl[269]