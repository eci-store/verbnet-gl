# Motion Classes

Notes on regularities found in Verbnet 3.3 motion classes and how to use them to generate GL Qualia and Event structures.

These are mostly notes to self, but cleaned up a bit, it gets rough after the **Agent Theme Initial_Location Destination** section.

Below are the roles defined for all verb classes with a motion predicate, using the following abbreviations: Ag=Agent, Th=Theme, Init=Initial_Location, Dest=Destination, Traj=Trajectory, Loc=Location, Res=Result, Src=Source and Instr=Instrument.

class                             | Ag | Th | Init | Dest | Traj | Loc | Res | Src | Goal | Instr 
--------------------------------- | -- | -- | ---- | ---- | ---- | --- | --- | --- | ---- | -----
accompany-51.7                    | +  | +  |      | +    |
assuming_position-50              | +  |    |      |      |      | +
bring-11.3                        | +  | +  | +    | +    |      |     |     |     |      | +
butter-9.9                        | +  | +  | +    | +   
carry-11.4                        | +  | +  | +    | +   
chase-51.6                        | +  | +  |      |      | +      
drive-11.5                        | +  | +  | +    | +   
escape-51.1                       |    | +  | +    | +    | +      
fill-9.8                          | +  | +  | +    | +   
funnel-9.3                        | +  | +  | +    | +   
leave-51.2                        |    | +  |      |      |      |     |     | +   | +
modes_of_being_with_motion-47.3   | +  | +  |      |      |      | +
nonvehicle-51.4.2                 | +  | +  |      |      | +      
pelt-17.2                         | +  | +  | +    | +   
pocket-9.10                       | +  | +  | +    | +   
pour-9.5                          | +  | +  | +    | +    
put-9.1                           | +  | +  | +    | +   
put_direction-9.4                 | +  | +  | +    | +   
put_spatial-9.2                   | +  | +  | +    | +   
reach-51.8                        |    | +  |      |      |      |     |     |     | +
roll-51.3.1                       | +  | +  |      |      | +    |     | +
run-51.3.2                        |    | +  | +    | +    | +    |
send-11.1                         | +  | +  | +    | +   
slide-11.2                        | +  | +  | +    | +    | +      
spray-9.7                         | +  | +  | +    | +   
throw-17.1                        | +  | +  | +    | +    |      |     | +
vehicle-51.4.1                    | +  | +  |      |      | +    |     | +
vehicle_path-51.4.3               | +  | +  | +    | +    | +    | 
waltz-51.5                        | +  | +  |      |      | +    |     |     |     | +

We will now discuss these in bunches, centered around common configurations of roles.


## Agent Theme Initial_Location Destination

This is the core case and includes the moving object (or objects), its initial location and its destination.

<!--
butter-9.9 carry-11.4 drive-11.5 fill-9.8 funnel-9.3 pelt-17.2 pocket-9.10 pour-9.5 put-9.1 put_direction-9.4
put_spatial-9.2 send-11.1 pray-9.7
-->

The theme always is a moving object and it is almost always epxressed in the subcategorisation (exceptions: butter-9.9, spray-9.7), in the predicates it shows up as

```
motion(during(E0), Theme)
```

The agent is often expressed and can be a moving object, if so, you will have

```
motion(during(E1), Agent)
euals(E0, E1)
```

Where	`E0` refers to the Theme.

Destination and Initial_Location may or may not be expressed. If expressed (for Agent and/or Theme) you will have:

```
path_rel(start(E0), Theme, Initial_Location, ch_of_loc, prep)
path_rel(end(E0), Theme, Destination, ch_of_loc, prep)
```

If not expressed in the subcat, you may still have a pathrel but now the role will have a question mark as a prefix:

```
path_rel(start(E), Theme, ?Initial_Location, ch_of_loc, prep)
path_rel(end(E0), Theme, Destination, ch_of_loc, prep)
```

<!--
There is a case where there is no motion:
	fill-9.8NP V NP, "The employees staffed the store."
	could still get At(e,s)
Well, I take that back, there can be motion, and it definitely is in the frame predicates.
-->

For the mapping to GL we basically take the Theme as the moving object and create two oppositions:

```
motion(e) 
Opposition(At(Th, Init), ¬At(Th, Init)) 
Opposition(¬At(Th, Dest), At(Th, Dest))
```

The variables are also used in the subcat (this is an addition to the Verbnet syntax):

```
Agent(Ag) V(e) Theme(Th) {(+src)} Initial_Location(Init) {to towards} Destination(Dest)
```

And for the event structure we get the following:

```
event(e)
initial_state(e, e1)
final_state(e, e2)
Holds-in(e1, At(Th, Init))
Holds-in(e2, At(Th, Dest))
```

When a role is not expressed in the subcat we use a variable name starting with 'x':

```
Agent(Ag) V(e) Theme(Th) {(+src)} Initial_Location(Init)

motion(e)
Opposition(At(Th, Init), ¬At(Th, Init))
Opposition(¬At(Th, x1), At(Th, x1))

event(e)
initial_state(e, e1)
final_state(e, e2)
Holds(e1, At(Th, Init))
Holds(e2, At(Th, x1))
```

If the Agent is also a moving object we simply add oppositions:

```
Agent(x1) V(e) Theme(x2) {(+src)} Initial_Location(x3) {to towards} Destination(x4)

motion(e) & Opposition(At(x2, x3), ¬¨At(x2, x3)) & Opposition(¬¨At(x2, x4), At(x2, x4))
& Opposition(At(x1, x3), ¬¨At(x1, x3)) & Opposition(¬¨At(x1, x4), At(x1, x4))
```


## Agent Theme Initial_Location Destination Instrument

bring-11.3

If Instrument is expressed then there is no Agent
There will be
	motion(during(E1), Instrument)
	path_rel(end(E1), Instrument, Destination, ch_of_loc, prep)
	equals(E0, E1)

The one frame with Instrument (NP V NP ADVP, "the train brought us here") also has a Destination
one could imagine a case without Destination ("the train took us away from there")
	

## Agent Theme Initial_Location Destination Result

throw-17.1

Result is never expressed and does not show in the predicates.


## Agent Theme Initial_Location Destination Trajectory

slide-11.2
vehicle_path-51.4.3

"Carla slid the books across the table."

See "Agent Theme Initial_Location Destination"

Extra Trajectory does not figure in an opposition.

However, we have either Trajectory location as intermediate state or Initial_Location and Destination as subregions of Trajectory.

Note that with pathrel the first argument and the role are linked in that we have the following pairs: 

```
<start(E1), Initial_Location>
<during(E1), Trajectory>
<end(E1), Destination>
```

Fore example

```
path_rel(start(E1), Agent, ?Initial_Location, ch_of_loc, prep)
path_rel(during(E1), Agent, ?Trajectory, ch_of_loc, prep)
path_rel(end(E1), Agent, ?Destination, ch_of_loc, prep)
```


## Agent Theme Location

modes_of_being_with_motion-47.3

"A flag fluttered over the fort."

These have a Theme in motion, but motion is in-place. No opposition, but we do have a location At(flag,fort).


## Agent Theme Trajectory

chase-51.6
nonvehicle-51.4.2

Similar to "Agent Theme Initial_Location Destination Trajectory".

Initial_Location and Destination
	Not expressewd, but still show up in pathrel
	"Jackie chased the thief down the street."

```
path_rel(start(E0), Theme, ?Initial_Location, ch_of_loc, prep)
path_rel(during(E0), Theme, Trajectory, ch_of_loc, prep)
path_rel(end(E0), Theme, ?Destination, ch_of_loc, prep)
```


## Agent Theme Trajectory Result

roll-51.3.1	"The drawer rolled open." (NP V ADJ)	
vehicle-51.4.1  "He skated Penny exhausted."              	

Result is not spatial in the second case, and probably not in the first either.

The subcat and predicates for the first are odd, not sure what the Source role is:

Subcategorisation

```
Theme(x1) V(e) Result(x2)
```

Predicates

```
motion(during(E), Theme)
path_rel(start(E), Theme, ?Source, ch_of_state, prep)
path_rel(end(E), Theme, Result, ch_of_state, prep)
```

Trajectory and Result are never used together.


## Agent Theme Trajectory Goal

waltz-51.5

"They waltzed across the room and into the hallway."

```
Theme(x1) V(e) {(+path)} Trajectory(x2) Goal(x3)
motion(during(E), Theme)
path_rel(start(E), Theme, ?Initial_Location, ch_of_loc, prep)
path_rel(during(E), Theme, Trajectory, ch_of_loc, prep)
path_rel(end(E), Theme, Goal, ch_of_loc, prep)
```

Why is Goal used instead of Destination?


#### Agent Theme Destination

accompany-51.7

See "Agent Theme Initial_Location Destination"



## Agent Location

assuming_position-50

"The dog flopped in the corner."

See "Agent Theme Location"

Motion is in-place.


## Theme Initial_Location Destination Trajectory

escape-51.1
run-51.3.2

See "Agent Theme Initial_Location Destination Trajectory"


## Theme Source Goal

leave-51.2

"She left her husband."
	
```
Theme(x1) V(e) Source(x2)
```

Predicates

```
motion(during(E), Theme)
	path_rel(start(E), Theme, Source, ch_of_loc, prep)
	path_rel(during(E), Theme, ?Trajectory, ch_of_loc, prep)
	path_rel(end(E), Theme, ?Goal, ch_of_loc, prep)
```

Source and Goal instead of Initial_Location and Destination. Are these cases for At(she, husband)?


## Theme Goal

reach-51.8

"They reached the hill."

Subcategorisation

```
Theme(x1) V(e) Goal(x2)
```

Predicates

```
motion(during(E), Theme)
path_rel(start(E), Theme, ?Source, ch_of_loc, prep)
path_rel(during(E), Theme, ?Trajectory, ch_of_loc, prep)
path_rel(end(E), Theme, Goal, ch_of_loc, prep)
```
