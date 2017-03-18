# verbnet-gl

Code to automatically expand VerbNet classes with GL qualia and event structure.

To run this you first need to get a version of VerbNet, this code was developed for version 3.3 so that's the version you should get. Then copy the file `config.sample.txt` to `config.txt` and edit the value of VERBNET_PATH to set the VerbNet directory. Then you can run the main program:

```
$ python verbnetgl.py
```

Results are written to `html/index.html`.
