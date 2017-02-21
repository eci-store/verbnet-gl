# verbnet-gl

Code to automatically expand VerbNet classes with GL qualia and event structure.

To run this you first need to get a version of VerbNet, this code was developed with versions 3.2.4 and 3.3 in mind.

Then copy the file `config.sample.txt` to `config.txt` and edit it to set the VerbNet directory:

```
$ cp config.sample.txt config.txt
$ YOUR_FAVOURITE_EDITOR config.txt
```

Then run the main program:

```
$ python verbnetgl.py
```

Results are written to `html/index.html`.
