"""
This file contains the class for James' Image Schema. These are schema used to 
identify subclasses of GL enhanced VerbNet classes, based on things such as 
specific PP heads used, Thematic Roles (Location, Destination, etc.), and
selectional restrictions on the PP head (src, loc, etc). Specific instances of 
these classes are then instantiated at the end of this file, to be used in an 
image search function in verbnetgl.py
"""

class ImageScheme(object):
    """Represents a single image scheme"""
    
    def __init__(self, name, pp_list, sel_res_list, role_list):
        self.name = name
        self.pp_list = pp_list
        self.sel_res_list = sel_res_list
        self.role_list = role_list
        
    def __repr__(self):
        return str(self.name) + "\nPP List: " + str(self.pp_list) + \
               "\nSelectional Restrictions: " + str(self.sel_res_list) + \
               "\nThematic Roles: " + str(self.role_list)


# Instantiated Schemes
               
# Location in Space
location_scheme = ImageScheme(
    "Location", 
    ["at", "on", "in"], 
    ["loc"], 
    ["Location"])

leftright_scheme = ImageScheme(
    "Left-Right",
    ["left-of", "right-of"], # Not in VerbNet
    ["loc"],
    ["Location"])

nearfar_scheme = ImageScheme(
    "Near-Far",
    ["near", "far"], # Not in VerbNet
    [],
    [])

updown_scheme = ImageScheme(
    "Verticality - Up-Down",
    ["above", "below", "up", "down"], # Not in VerbNet
    ["loc"],
    ["Location"])

contact_scheme = ImageScheme(
    "Contact-No Contact",
    ["on", "in"],
    ["loc"],
    ["Destination"])

frontbehind_scheme = ImageScheme(
    "In front of - Behind",
    ["front", "behind"], # Not in VerbNet
    ["loc"],
    ["Location"])

# Movement through Space
# motion_scheme uses manner adverbials of speed e.g. quickly, slowly

path_scheme = ImageScheme(
    "Path",
    ["on", "along", "through"], # Along not in VerbNet
    ["path"],
    ["Trajectory"])
                              
start_scheme = ImageScheme(
    "Start (Source)",
    ["from"],
    ["src", "path"],
    ["Initial_Location"])

end_scheme = ImageScheme(
    "End (Goal)",
    ["at", "to"],
    [],
    ["Destination"])

directional_scheme = ImageScheme(
    "Directional",
    ["to", "towards", "away", "for"], # away, toward not in VN
    ["dest_dir", "dest_conf"],
    ["Destination"])

# Containment
container_scheme = ImageScheme(
    "Container",
    ["in", "into", "inside"], # inside not in VN
    [],
    [])

surface_scheme = ImageScheme(
    "Surface",
    ["over", "on"],
    [],
    [])


SCHEME_LIST = [location_scheme, leftright_scheme, nearfar_scheme, 
               updown_scheme, contact_scheme, frontbehind_scheme, 
               path_scheme, start_scheme, end_scheme, directional_scheme, 
               container_scheme, surface_scheme]