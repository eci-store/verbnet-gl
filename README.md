# verbnet-gl

Code to manipulate VerbNet classes and to extract information from them. There are two main top-level functionalities:

1. Expanding VerbNet classes with GL qualia and event structure.
2. Extracting selectional restrictions.

To run either of these you first need to get a version of VerbNet, this code was developed for version 3.3 so that's the version you should get. Then copy the file `config.sample.txt` to `config.txt` and edit the value of VERBNET_PATH to set the VerbNet directory.


### Expanding VerbNet classes

The main program for this is `verbnetgl.py` which you simply run as follows:

```
$ python verbnetgl.py
```

Results are written to `html/index.html`. See the documentation string in `verbnetgp.py` for command lines options and other details.


### Extracting selectional restrictions

The goal here is to extract restrictions from frames and then link them to elements of example sentences. To run it:

```
$ python restrictions.py
```

Parameters for the script are controlled by setting a couple of global variables at the top of the script, see the document string of the script for a description.

The selectional restrictions code requires installation of the [TreeTagger](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/).
