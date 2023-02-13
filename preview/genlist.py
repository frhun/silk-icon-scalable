#!/bin/python

import glob
import os
import re

originalpngpath = "famfamfam_silk_icons_v013/icons/"

def genlisthtml(print):
    assert (os.path.basename(os.getcwd()) != "preview" and os.path.exists("./preview")), \
        "This script has to be run from the base directory. (i.e. the path containing the preview directory)"

    basepath = "generate/target/"
    iconcategories = [{"name": "Base Set", "path": ""}, {"name": "Extra Icons", "path": "extra/"}]

    print("<!-- Generated code starts here -->")

    for iconcategory in iconcategories:

        def outputIconDivs(pathprefix):
            svgs = glob.glob(pathprefix + "*.svg")
            svgbasenames = [os.path.basename(svgname) for svgname in svgs]
            svgbasenames.sort()
            originalpngs = [os.path.basename(filename) for filename in glob.glob(originalpngpath + "*.png")]
            for matchingsvg in svgbasenames:
                originalpng = matchingsvg.replace(".svg", ".png")
                if originalpng in originalpngs:
                    imagehtml = "<img src=\"{0}\" class=\"originalcomparison\" />".format("../" + originalpngpath + originalpng)
                else:
                    imagehtml = ""

                print(
                    """
                    <div class=\"iconcontainer\">
                        <img src=\"../{0}\" alt=\"{1}\" />
                        {2}
                        <p>{1}</p>
                    </div>"""
                    .format(pathprefix + matchingsvg, matchingsvg, imagehtml)
                )

        print("<h2>%s</h2>\n<div class=\"iconclass\">" % (iconcategory["name"]))
        outputIconDivs(basepath + iconcategory["path"])
        print("</div>")

    print("<!-- Generated code ends here -->")

if __name__ == "__main__":
    genlisthtml(print)