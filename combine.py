#!/bin/env pyhton
import yaml
import os
from os import path as p
from io import open as openfile
import glob
import subprocess
import sys
import copy
from concurrent.futures import ThreadPoolExecutor, wait
import multiprocessing
import svgutils.transform as svgtransform

"""
Technical Debt Note:
 - the presence of the 'svgo' and 'inkscape' commands and
   their accessability is assumed (https://github.com/svg/svgo)
 - paths are not checked for safety, i.e. if they point to outside the build directory
"""


def svgoTreat(inFile, outFile=""):
    if p.isfile(inFile) and True if outFile=="" else p.isdir(p.dirname(outFile)):
        args = ["svgo", inFile]
        if(outFile != ""):
            args.append(["-o", outFile])
        subprocess.run(args)
    else:
        print("A non existing file path was passed to svgoTreat().", file=sys.stderr)
        exit(2)

def svgoTreatPath(inPath, outPath=""):
    if p.isdir(inPath) and True if outPath=="" else p.isdir(outPath):
        args = ["svgo", "-f", inPath]
        if(outPath != ""):
            args.append("-o", outPath)
        subprocess.run(args)
    else:
        print("A non existing directory path was passed to svgoTreatPath().", file=sys.stderr)
        exit(2)

def inkscapeExportNormal(inFile, outFile):
    if p.isfile(inFile) and p.isdir(p.dirname(outFile)):
        subprocess.run(["inkscape", "--export-plain-svg", "--vacuum-defs",
                        "--export-text-to-path", "-o", outFile, inFile])
    else:
        print("A non existing file path was passed to inkscapeExportNormal().", file=sys.stderr)
        exit(2)

def createNeededDir(dirPath):
    if not p.exists(dirPath):
        os.makedirs(dirPath)

def conditionStringPath(stringFromYaml):
    return p.join(*stringFromYaml.split("/"))

def safePath(path):
    """
    Makes the path absolute, and checks if it stays within the bounds of the cwd.
    If not, it throws an error.
    To make sure there are no write operations outside the project directory,
    apply this function to every path used as a write operation destination.
    """
    path = p.abspath(path)
    if not path.startswith(os.getcwd()):
        raise ValueError("An output path was unsafe, by pointing outside the cwd.")
    return path

gendirname = "generate"
overlaydirname = "overlays"
layerdirname = "layers"
srcexportdirname = "baseexport"
artifactdirname = "target"
svgext = ".svg"
sourcesvgpaths = [".", overlaydirname, layerdirname, "extra", "extraoverlays", "baseicons"]
neededpaths = [gendirname, p.join(gendirname, srcexportdirname)]

if __name__ == "__main__":
    for path in neededpaths:
        createNeededDir(path)

    config = yaml.load(open("icongen.yaml", "r"), Loader=yaml.SafeLoader)

    if True:
        for srcdirname in sourcesvgpaths:
            createNeededDir(p.join(".", gendirname, srcexportdirname, srcdirname))
            with ThreadPoolExecutor(max_workers=max(1, multiprocessing.cpu_count() - 2)) as executor:
                futures = []
                def processSrcSvg(srcsvg, outFilePath):
                    inkscapeExportNormal(srcsvg, outFilePath)
                    svgoTreat(outFilePath)
                for srcsvg in glob.glob(p.join(".", srcdirname, "*.svg")):
                    outFilePath = safePath(p.join(".", gendirname, srcexportdirname,
                                         srcdirname, p.basename(srcsvg)))
                    futures.append(executor.submit(processSrcSvg, srcsvg, outFilePath))
                wait(futures)
    
    for exportMapping in config["export-mappings"]:
        if exportMapping["type"] == "overlays":
            basepath = conditionStringPath(exportMapping.get("basepath", "./"))
            overlayspath = conditionStringPath(exportMapping["overlayspath"])
            outputpath = conditionStringPath(exportMapping["outputpath"])
            createNeededDir(p.join(gendirname, artifactdirname, outputpath))
            for baselayer in exportMapping["baselayers"]:
                baselayerName = baselayer["name"]
                baselayersvgpath = p.abspath(p.join(gendirname, srcexportdirname,
                                                    basepath, baselayerName)
                                             + svgext)
                baselayersvg = svgtransform.fromfile(baselayersvgpath)
                for overlayvariant in baselayer["overlays"]:
                    outname = overlayvariant["outname"]
                    if(overlayvariant["outname-type"] == "append"):
                        outname = baselayerName + outname
                    outputFilePath = safePath(p.join(gendirname, artifactdirname,
                                            outputpath, outname) + svgext)
                    layeredSvg = copy.deepcopy(baselayersvg)
                    overlaysvgpath = p.abspath(p.join(gendirname, srcexportdirname,
                                                      overlayspath, overlayvariant["overlay"])
                                               + svgext)
                    overlaysvg = svgtransform.fromfile(overlaysvgpath)
                    layeredSvg.append(overlaysvg)
                    layeredSvg.save(outputFilePath)
                    svgoTreat(outputFilePath)

        elif exportMapping["type"] == "hardlink":
            outputpath = safePath(p.join(gendirname, artifactdirname, conditionStringPath(exportMapping.get("outputpath", "./"))))
            createNeededDir(outputpath)
            globexpr = p.abspath(p.join(gendirname, srcexportdirname,
                                    conditionStringPath(exportMapping["glob"]) + svgext))
            for file in glob.glob(globexpr):
                outputlinkpath = safePath(p.join(outputpath, p.basename(file)))
                if p.exists(outputlinkpath):
                    os.remove(outputlinkpath)
                os.link(p.abspath(file), outputlinkpath)