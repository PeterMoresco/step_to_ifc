'''
This is a macro to transform the selected STEP obj to a IFC,
with the same tree structure and geometries.
'''
# TODO Change the name of the original object before the new
# TODO Change the IFC type
# TODO Checks the properties for the IFC


from tempfile import NamedTemporaryFile
import os
import time
import argparse
import logging
import platform
import sys
from PySide2 import QtCore, QtGui, QtWidgets
import FreeCAD
import Arch
import FreeCADGui


class MainWindow(QtWidgets.QMainWindow):
    def showEvent(self, event):
        FreeCADGui.showMainWindow()
        self.setCentralWidget(FreeCADGui.getMainWindow())


def add_children(obj, container):
    # Get the children
    children = obj.OutList
    for child in children:
        # Check the type
        if child.TypeId == 'App::Part':  # Assembly
            # Create the container
            subCont = make_b_part(child)
            # Adds the child to the dad
            container.addObject(subCont)
            if len(child.OutList) != 0:
                add_children(child, subCont)
        elif child.TypeId == 'Part::Feature':  # Part/Component
            # Make the component
            component = make_component(child)
            # Adds to its parent
            container.addObject(component)


def make_component(item):
    # Create the component
    component = Arch.makeComponent(item)
    # Change the label
    component.Label = item.Label
    # Change the placement
    component.Placement = item.getGlobalPlacement()
    return component


def make_b_part(item):
    # Create the container
    container = Arch.makeBuildingPart()
    # Copy the placement
    container.Placement = item.Placement.copy()
    # Copy the label
    container.Label = item.Label
    return container


def step_to_ifc(obj):
    # Create the main container
    cont = make_b_part(obj)
    # Add the children to the tree of the dad
    add_children(obj, cont)
    return cont


def select_bigger_container():
    # Get all the container objects in the tree
    containers = list(filter(lambda x: x.TypeId ==
                      'App::Part', FreeCAD.ActiveDocument.Objects))
    # Gets the children count
    childrenCount = [len(x.OutListRecursive) for x in containers]
    # Sort them
    sortedList = [x for _, x in sorted(
        zip(childrenCount, containers), key=lambda duo: duo[0])]
    # The main container
    return sortedList[-1]


def import_step(filePath, nDocName):
    # Check filepath
    if not os.path.exists(filePath):
        raise Exception('Filepath {} invalid.'.format(filePath))
    import ImportGui
    ImportGui.insert(filePath, nDocName)


def export_ifc(obj, filePath):
    # Create the list to hold the objects
    __objs__ = []
    # Collect the items
    __objs__.append(FreeCAD.ActiveDocument.getObject(obj.Name))
    # Export the item
    import exportIFC
    exportIFC.export(__objs__, filePath)


def convert_obj(stepPath, ifcPath):
    # This code is needed in order to
    # some functionalities to work properly
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.resize(1200, 800)
    # Find this option on Stack Overflow 
    # And the result is better than using ".show()"
    mw.showMinimized()
    # mw.show()
    fVersion = FreeCAD.Version()
    logging.info('Using FreeCAD v{}.{} build {}'.format(
        fVersion[0], fVersion[1], fVersion[2]))
    logging.info('Started the UI')
    # Initiates a new document
    newDocName = 'TempPart'
    FreeCAD.newDocument(newDocName)
    logging.info('Created a new document')
    FreeCADGui.activateWorkbench("ArchWorkbench")
    # The document must been save before in order
    # To do not open the saveas popup
    tempFile = NamedTemporaryFile(suffix='.FCStd', delete=True)
    tempname = tempFile.name
    FreeCAD.getDocument(newDocName).saveAs(tempname)
    # Import step file
    logging.info('Started to import the STEP file')
    import_step(stepPath, newDocName)
    logging.info('Finished to load the STEP file')
    # Gets the object
    obj = select_bigger_container()
    logging.info('Selected the "{}" container'.format(obj.Label))
    partEnt = list(filter(lambda x: x.TypeId ==
                   'Part::Feature', obj.OutListRecursive))
    contEnt = list(filter(lambda x: x.TypeId ==
                   'App::Part', obj.OutListRecursive))
    logging.info(
        'The STEP file contains {} part(s) and {} container(s)'.format(len(partEnt), len(contEnt)))
    # Creates the IFC object
    logging.info('Started the creation of the IFC objects')
    ifcContainer = step_to_ifc(obj)
    logging.info('Finished creating the IFC objects')
    # Export the IFC
    logging.info('Starting to export the IFC file')
    export_ifc(ifcContainer, ifcPath)
    logging.info('Finished exporting the IFC file')
    # Close the document
    logging.info('Closing the document')
    FreeCAD.closeDocument(newDocName)


def totalRAM():
    '''
    This function calculates the total amount of RAM, 
    using only standard librabries. It's not pretty.
    '''
    process = os.popen('wmic memorychip get capacity')
    result = process.read()
    process.close()
    try:
        totalMem = float(result.replace(
            '\n', '').strip().split(' ')[-1])/1024**3
        return totalMem
    except:
        return 'NA'

def getNode(_root, nodeName):
    '''
    A simple function to return the value from an XPath
    query
    '''
    # Try to get the value from the XML three
    node = _root.findall(".//*[@Name='{}']".format(nodeName))
    if len(node) == 1:
        return node[0].get('Value')
    else:
        return 'NA'

def getIFCExportPreferences():
    '''
    Retrieves the export IFC preferences from FreeCAD.
    Since the approach used by exportIFC.py I could not make
    to work, I found a workaround based on the post
    https://forum.freecadweb.org/viewtopic.php?t=37524
    '''
    # I discover this by exploring the options for FreeCAD 
    # in the console
    # Get the path to the user.cfg
    userCfgFolder = FreeCAD.getUserAppDataDir()
    userCfgFile = os.path.join(userCfgFolder, 'user.cfg')
    if not os.path.exists(userCfgFile):
        logging.info('The user configuration file was not found')
    else:
        logging.info('The user configuration file is on {}'.format(userCfgFolder))
        import xml.etree.ElementTree as ET
        tree = ET.parse(userCfgFile)
        root = tree.getroot()
        # STEP import options
        # Compound merge
        compMerge = 'on' if getNode(root, 'ReadShapeCompoundMode') == '1' else 'off'
        logging.info('The option to merge compound is {}'.format(compMerge))
        # Link group
        linkGroup = 'on' if getNode(root, 'UseLinkGroup') == '1' else 'off'
        logging.info('The option to use link group is {}'.format(linkGroup))
        # Import invisible objects
        invObj = 'on' if getNode(root, 'ImportHiddenObject') == '1' else 'off'
        logging.info('The option to import invisible objects is {}'.format(invObj))
        # Reduce number of objects
        redObj = 'on' if getNode(root, 'ReduceObjects') == '1' else 'off'
        logging.info('The option to reduce the number of objects is {}'.format(redObj))
        # Expand compound shape
        expComp = 'on' if getNode(root, 'ExpandCompound') == '1' else 'off'
        logging.info('The option to expand compund shapes is {}'.format(expComp))
        # Show progressbar
        progBar = 'on' if getNode(root, 'ShowProgress') == '1' else 'off'
        logging.info('The option to show the progressbar is {}'.format(progBar))
        # ignore names
        igNames = 'on' if getNode(root, 'UseBaseName') == '1' else 'off'
        logging.info('The option to ignore the instances names is {}'.format(igNames))
        # Get the STEP mode option
        stepMode = ['Single document',
                    'Assembly per document',
                    'Assembly per document in sub-directory',
                    'Object per document',
                    'Object per document in sub-directory'][int(getNode(root, 'ImportMode'))]
        logging.info('The STEP import mode option is set to {}'.format(stepMode))
        # IFC export options
        # Show dialog when importing
        showDiag = 'on' if getNode(root, 'ifcShowDialog') == '1' else 'off'
        logging.info('The option to show the dialog window when exporting is {}'.format(showDiag))
        # Get the debug option
        debug = 'on' if getNode(root, 'ifcDebug') == '1' else 'off'
        logging.info('The option to debug the ifc export is {}'.format(debug))
        # Number of processors to use
        nProc = '1' if getNode(root, 'ifcMulticore') == '0' else getNode(root, 'ifcMulticore')
        logging.info('The number of processors to use is {}'.format(nProc))
        # Export type
        exptype = ['Standard Model', 'Structural analysis', 'Standard + Structural'][int(getNode(root, 'ifcExportModel'))]
        logging.info('The export type option is set to {}'.format(exptype))
        # Brep option
        brep = 'on' if getNode(root, 'ifcExportAsBrep') == '1' else 'off'
        logging.info('The option to force the use of Brep geometries is {}'.format(brep))
        # DAE triangulations
        dae = 'on'  if getNode(root, 'ifcUseDaeOptions') == '1' else 'off'
        logging.info('The option to use DAE triangulation is {}'.format(dae))
        # Join coplanar faces
        jfaces = 'on' if getNode(root, 'ifcJoinCoplanarFacets') == '1' else 'off'
        logging.info('The option to join coplanar faces is {}'.format(jfaces))
        # Store UID
        uid = 'on' if getNode(root, 'ifcStoreUid') == '1' else 'off'
        logging.info('The option to store the UID is {}'.format(uid))
        # Use the ifcopenshell serializer
        OSserial = 'on' if getNode(root, 'ifcSerialize') == '1' else 'off'
        logging.info('The option to use the IfcOpenShell serializer is {}'.format(OSserial))
        # Export 2D annotations
        anottations = 'on' if getNode(root, 'ifcExport2D') == '1' else 'off'
        logging.info('The option to export the 2D annotations is {}'.format(anottations))
        # FreeCAD full model
        fmodel = 'on' if getNode(root, 'IfcExportFreeCADProperties') == '1' else 'off'
        logging.info('Export full parametric FreeCAD model is {}'.format(fmodel))
        # Get the clone option
        clone = 'on' if getNode(root, 'ifcCompress') == '1' else 'off'
        logging.info('The option to create clones from entities is {}'.format(clone)) 
        # Disable ifcRect...
        ifcRPD = 'on' if getNode(root, 'DisableIfcRectangleProfileDef') == '1' else 'off'
        logging.info('The option to disable the rectangle profile def is {}'.format(ifcRPD))
        # Default type    
        dtype = 'on' if getNode(root, 'getStandardCase') == '1' else 'off'
        logging.info('The option to use standard types is {}'.format(dtype))
        # Add Site
        dsite = 'on' if getNode(root, 'IfcAddDefaultSite') == '1' else 'off'
        logging.info('The option to add a default site is {}'.format(dsite))
        # Add building
        dbuild = 'on' if getNode(root, 'IfcAddDefaultBuilding') == '1' else 'off'
        logging.info('The option to add a default building is {}'.format(dbuild))
        # Add Store
        dstore = 'on' if getNode(root, 'IfcAddDefaultStorey') == '1' else 'off'
        logging.info('The option to add a default store is {}'.format(dstore))
        # Get the unit
        unitType = 'metric' if getNode(root, 'ifcUnit') == '0' else 'foot'
        logging.info('The units of the ifc export are set to {}'.format(unitType))
    

def main():
    '''
    This function wraps the argparser and 
    initiate the logging
    '''
    # Create the parser
    my_parser = argparse.ArgumentParser(
        description='Convert a STEP assembly to IFC.')
    # Add the arguments
    my_parser.add_argument('step_fpath',
                           metavar='step_fpath',
                           type=str,
                           help='Path to the STEP file')
    my_parser.add_argument('ifc_fpath',
                           metavar='ifc_fpath',
                           type=str,
                           help='Path to the output ifc file')
    # Parse the args
    args = my_parser.parse_args()

    stepFpath = args.step_fpath
    ifcFpath = args.ifc_fpath

    # Checks the extension of the IFC
    # To ensure that the log will not conflict with the ifc filename
    if not ifcFpath.endswith('.ifc'):
        raise Exception('The IFC filename must end with ".ifc"')

    # Creates the name of the log file
    logFname = ifcFpath.replace('.ifc', '.log')
    # Starts the logging setup
    logging.basicConfig(filename=logFname, level=logging.INFO, filemode='w',
                        format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%H:%M:%S')
    # Check the input step file path
    if not os.path.exists(stepFpath):
        logging.error('Theres no file with the path {}'.format(stepFpath))
        raise Exception('Theres no file {}'.format(stepFpath))

    # Log file head info
    logging.info(
        'Startig the process to convert the file "{}"'.format(stepFpath))
    logging.info('OS: {}'.format(platform.platform()))
    logging.info('Machine name: {}'.format(platform.node()))
    logging.info('Processor: {}'.format(platform.processor()))
    logging.info('Total RAM amount: {} Gb'.format(totalRAM()))
    # Get the export IFC settings
    getIFCExportPreferences()
    # Start the time counting
    startProc = time.time()

    convert_obj(stepFpath, ifcFpath)

    logging.info('The original STEP file was {:.2f} MB big'.format(
        os.path.getsize(stepFpath)/1024**2))
    logging.info('The generated IFC file is {:.2f} MB big'.format(
        os.path.getsize(ifcFpath)/1024**2))
    logging.info('The entire process took {:.1f} minutes'.format(
        (time.time() - startProc)/60))


if __name__ == '__main__':
    main()
