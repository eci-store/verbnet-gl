
# Some issues found in the motion classes

### 1. Incorrect theme in butter-9.9?

Note that for "Lora buttered the toast" we get

```
motion(during(E), Theme)
path_rel(start(E), Theme, ?Initial_Location, ch_of_loc, prep)
path_rel(end(E), Theme, Destination, ch_of_loc, prep)
```

while the subcat says

```
Agent V Destination
```

Not sure why `Theme` is not `?Theme`. Compare this with spray-9.7, "Jessica sprayed the wall":

```
motion(during(E), ?Theme)
path_rel(start(E), ?Theme, ?Initial_Location, ch_of_loc, prep)
path_rel(end(E), ?Theme, Destination, ch_of_loc, prep)
```

with subcat

```
Agent V Destination
```

Here we indeed have `?Theme` instead of `Theme`


### 2. Goal that appears to be a Result

In waltz-51.5 there are the following two frames

1. NP V NP ADJP |"He waltzed her dizzy."
2. NP V NP PP.goal |Example	"He waltzed her to exhaustion."

The ADVP or PP.goal is presented as a goal of the motion.

```
Agent V Theme Goal
motion(during(E), Theme)
cause(Agent, E)
path_rel(start(E), Agent, ?Source, ch_of_loc, prep)
path_rel(end(E), Theme, Goal, ch_of_loc, prep)
```

Here, `Goal` does not appear to be a location. In addition there is the `?Source` which incidentally is not expressed in the roles list of the verb class.

Note that this contrasts with vehicle-51.4.1 "He skated Penny exhausted.", where `Result` is used as expected.

```
motion(during(E), Theme)
path_rel(start(E), Theme, ?Source, ch_of_state, prep)
path_rel(end(E), Theme, Result, ch_of_state, prep)
```

Not sure about the use of `path_rel` though.
