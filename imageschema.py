"""imageschema.py

This file contains the class for James' Image Schema. These are schema used to 
identify subclasses of GL enhanced VerbNet classes, based on things such as 
specific PP heads used, Thematic Roles (Location, Destination, etc.), and
selectional restrictions on the PP head (src, loc, etc). Specific instances of 
these classes are then instantiated at the end of this file, to be used in an 
image search function in verbnetgl.py

The main function is create_schema_to_verbnet_mappings(), which creates a bunch
of html pages with mappnigs between image schema and VerbNet.

"""

from verbnetparser import VerbNetParser
import verbnetgl
from writer import HtmlWriter, HtmlClassWriter
from search import search_by_predicate, search_by_argtype
from search import search_by_ID, search_by_subclass_ID
from search import search_by_themroles, search_by_POS, search_by_cat_and_role
from search import reverse_image_search, image_schema_search, image_schema_search2


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


SCHEME_LIST = [
    
    ImageScheme("Location", ["at", "on", "in"], ["loc"], ["Location"]),

     # Not in VerbNet
    ImageScheme("Left-Right", ["left-of", "right-of"], ["loc"], ["Location"]),

    # Not in VerbNet
    ImageScheme("Near-Far", ["near", "far"], [], []),

    # Not in VerbNet
    ImageScheme("Up-Down", ["above", "below", "up", "down"], ["loc"], ["Location"]),

    ImageScheme("Contact-No Contact", ["on", "in"], ["loc"], ["Destination"]),

    # Not in VerbNet
    ImageScheme("Front-Behind", ["front", "behind"], ["loc"], ["Location"]),

    # Movement through Space
    # motion_scheme uses manner adverbials of speed e.g. quickly, slowly
    # Along not in VerbNet
    ImageScheme("Path", ["on", "along", "through"], ["path"], ["Trajectory"]),
                              
    ImageScheme("Start (Source)", ["from"], ["src", "path"], ["Initial_Location"]),

    ImageScheme("End (Goal)", ["at", "to"], [], ["Destination"]),

    # away, toward not in VN
    ImageScheme("Directional", ["to", "towards", "away", "for"], ["dest_dir", "dest_conf"], ["Destination"]),

    # inside not in VN
    ImageScheme("Container", ["in", "into", "inside"], [], []),

    ImageScheme("Surface", ["over", "on"], [], [])
]


# The following five functions should probably be moved to writer.py, but they
# cannot be moved as is because of dependencies to methods in this file. Some
# refactoring is needed.

def pp_image_search_html(verbclasslist, results):
    """Uses a list of [image_search_name, search_results]"""
    INDEX = open('html/image_search_index.html', 'w')
    pp_html_begin(INDEX)
    for result in results:
        scheme = result[0]
        INDEX.write("<tr class=header><td>%s</a>\n" % scheme.name)
        INDEX.write("<tr class=header><td>PP List: %s</a>\n" % scheme.pp_list)
        INDEX.write("<tr class=header><td>Selectional Restrictions: %s</a>\n" % scheme.sel_res_list)
        INDEX.write("<tr class=header><td>Thematic Roles: %s</a>\n" % scheme.role_list)
        if len(results[1]) == 0:
            INDEX.write("<tr class=body><td>No Results\n")
        for vc_id, class_results in result[1]:
            id_dict = {}
            for frame,frame_num,ID in class_results:
                results_type = []
                for member in frame.subcat:
                    if member.cat == "PREP":
                        if len(member.role) > 0:
                            if member.role[0] in scheme.pp_list:
                                results_type.append("PP")
                        if len(member.sel_res) > 0:
                            for res in member.sel_res:
                                if res in scheme.sel_res_list:
                                    results_type.append("SR")
                    if len(member.role) > 0:
                        if member.role[0] in scheme.role_list:
                            results_type.append("TR")
                if ID in id_dict:
                    id_dict[ID].append((frame_num, results_type))
                else:
                    id_dict[ID] = [(frame_num, results_type)]
            for ID in id_dict.keys():
                class_file = "imageresult-%s.html" % ID
                INDEX.write("<tr class=body><td><a href=\"%s\">%s</a>\n" % (class_file, ID))
                INDEX.write("  <td>")
                for frame_num,results_type in sorted(id_dict[ID]):
                    INDEX.write("Frame %s" % frame_num)
                    for result in results_type:
                        INDEX.write("<sup>%s</sup> " % result)
                    INDEX.write("&emsp;")
                VNCLASS = open("html/%s" % class_file, 'w')
                verbclass = search_by_ID(verbclasslist, ID)
                class_writer = HtmlClassWriter(VNCLASS, verbclass)
                frame_numbers = sorted([num for num,type in id_dict[ID]])
                class_writer.write(frames=frame_numbers)
    pp_html_end(INDEX)


def pp_reverse_image_search_html(verbclasslist, frame_list, scheme_list):
    INDEX = open('html/image_search_reverse_index.html', 'w')
    pp_html_begin(INDEX)
    INDEX.write("<tr class=header><td>Reverse Image Search Results:\n</a>")
    for frame,frame_num,ID in sorted(set(frame_list)):
        results = []
        for scheme in scheme_list:
            if reverse_image_search(frame, scheme):
                results.append(scheme.name)
        INDEX.write("<tr class=body><td>%s</a>" % ID)
        class_file = "imageresultreverse-%s_frame%s.html" % (ID, frame_num)
        INDEX.write("<a href=\"%s\"> - Frame %s</a>" % (class_file, frame_num))
        INDEX.write("  <td>")
        if len(results) == 0:
            INDEX.write("-\n")
        for i in range(len(results)):
            if i < len(results) - 1:
                INDEX.write("%s, " % results[i])
            else:
                INDEX.write("%s\n" % results[i])
        VNCLASS = open("html/%s" % class_file, 'w')
        verbclass = search_by_ID(verbclasslist, ID)
        class_writer = HtmlClassWriter(VNCLASS, verbclass)
        class_writer.write(frames=[frame_num])
    pp_html_end(INDEX)


def pp_reverse_image_bins_html(verbclasslist, frame_list, scheme_list):
    INDEX = open('html/image_search_bins_index.html', 'w')
    pp_html_begin(INDEX)
    image_bins = dict()
    for frame,frame_num,ID in sorted(set(frame_list)):
        results = set()
        for scheme in scheme_list:
            if reverse_image_search(frame, scheme):
                results.add(scheme.name)
        if frozenset(results) in image_bins.keys():
            image_bins[frozenset(results)].append((frame, frame_num, ID))
        else:
            image_bins[frozenset(results)] = [(frame, frame_num, ID)]
    for bin in image_bins.keys():
        INDEX.write("<tr class=header><td></a>")
        if len(bin) == 0:
            INDEX.write("PP Only Frames:")
        for scheme in bin:
            INDEX.write("%s&emsp;" % scheme)
        INDEX.write("<tr class=body><td></a>")
        for frame, frame_num, ID in image_bins[bin]:
            class_file = "imageresultbins-%s_frame%s.html" % (ID, frame_num)
            INDEX.write("<a href=\"%s\">%s<sup>%s&emsp;</sup></a>" % (class_file, ID, frame_num))
            VNCLASS = open("html/%s" % class_file, 'w')
            verbclass = search_by_ID(verbclasslist, ID)
            class_writer = HtmlClassWriter(VNCLASS, verbclass)
            class_writer.write(frames=[frame_num])
    pp_html_end(INDEX)


def pp_html_begin(fh):
    fh.write("<html>\n")
    fh.write("<head>\n")
    fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
    fh.write("</head>\n")
    fh.write("<body>\n")
    fh.write("<table cellpadding=8 cellspacing=0>\n")


def pp_html_end(fh):
    fh.write("</table>\n")
    fh.write("</body>\n")
    fh.write("</html>\n")

    
def test_image_searches(vn_classes):
    # figure out left-of right-of
    # figure out advs of speed
    print
    for print_string, pp_list, sem_list in [
            ("in at on destination:", ['in', 'at', 'on'], ['Destination']),
            ("in at on location:", ['in', 'at', 'on'], ['Location']),
            ("near far:", ['near', 'far'], None),
            ("up-down:", ['up', 'down', 'above', 'below'], None),
            ("Contact No-Contact on in:", ['on', 'in'], None),
            ("Front/Behind:", ['front', 'behind'], None),
            ("Path along on:", ['along', 'on'], None),
            ("Source from:", ['from'], ['Initial_Location']),
            ("End at to:", ['at', 'to'], ['Destination']),
            ("Directional toward away for:", ['toward', 'away', 'for'], ['Source']),
            ("Container in inside:", ['in', 'inside'], None),
            ("Surface over on:", ['over', 'on'], None) ]:
        results = image_schema_search2(vn_classes, pp_list, sem_list)
        print print_string
        print [vcid for frame, vcid in results], len(results), "\n"


def new_image_searches(vn_classes):
    results = []
    for scheme in SCHEME_LIST:
        result = image_schema_search(vn_classes, scheme)
        results.append((scheme, result))
    return results


def reverse_image_frame_list(vn_classes):
    image_results = new_image_searches(vn_classes)
    frame_list = []
    for scheme, results in image_results:
        for vc_id, class_results in results:
            for frame,frame_num,ID in class_results:
                frame_list.append((frame, frame_num, ID))
    return frame_list


def create_schema_to_verbnet_mappings(vn_classes):
    image_results = new_image_searches(vn_classes)
    frames = reverse_image_frame_list(vn_classes)
    pp_image_search_html(vn_classes, image_results)
    pp_reverse_image_search_html(vn_classes, frames, SCHEME_LIST)
    pp_reverse_image_bins_html(vn_classes, frames, SCHEME_LIST)



if __name__ == '__main__':

    vn = VerbNetParser(max_count=50)
    #vn = VerbNetParser(file_list='list-motion-classes.txt')
    #vn = VerbNetParser(file_list='list-random.txt')
    #vn = VerbNetParser()
    vn_classes = [verbnetgl.GLVerbClass(vc) for vc in vn.verb_classes]

    test_image_searches(vn_classes)
    create_schema_to_verbnet_mappings(vn_classes)
