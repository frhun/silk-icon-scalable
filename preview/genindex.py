#!/bin/python

import os
import re
import genlist

def genindex():
    assert (os.path.basename(os.getcwd()) != "preview" and os.path.exists("./preview")), \
        "This script has to be run from the base directory. (i.e. the path containing the preview directory)"

    #assert os.path.exists("./preview/list.htmlpart"), "Could not generate Index, because the substitution content could not be found"

    #htmlpart = open("./preview/list.htmlpart", mode="r")
    template = open("./preview/preview.html")

    listhtml = list()

    def addtolisthtml(addtxt):
        listhtml.append(addtxt + "\n")
    
    genlist.genlisthtml(addtolisthtml)

    htmltext = template.read()

    #indextext = re.sub("<slot>[\\s\\S]*</slot>", htmlpart.read(), htmltext)
    indextext = re.sub("<slot>[\\s\\S]*</slot>", "".join(listhtml), htmltext)

    indexfile = open("./preview/index.html", "w")
    indexfile.write(indextext)

    #htmlpart.close()
    template.close()
    indexfile.close()

if __name__ == "__main__":
    genindex()