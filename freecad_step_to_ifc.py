'''
This is a macro to transform the selected STEP obj to a IFC,
with the same tree structure and geometries.
'''
# TODO Change the name of the original object before the new
# TODO Change the IFC type
# TODO Add the headless functionality
# TODO Checks the properties for the IFC


from tempfile import NamedTemporaryFile
import os
import argparse
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
            # COMM
            print('Adding {} to {}'.format(
                component.Label, container.Label))
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
    import os.path
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
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.resize(1200, 800)
    mw.show()
    # Initiates a new document
    newDocName = 'TempPart'
    FreeCAD.newDocument(newDocName)
    FreeCADGui.activateWorkbench("ArchWorkbench")
    # The document must been save before in order
    # To do not open the saveas popup
    tempFile = NamedTemporaryFile(suffix='.FCStd', delete=True)
    tempname = tempFile.name
    FreeCAD.getDocument(newDocName).saveAs(tempname)
    # Import step file
    import_step(stepPath, newDocName)
    # Gets the object
    obj = select_bigger_container()
    # Creates the IFC object
    ifcContainer = step_to_ifc(obj)
    # Export the IFC
    export_ifc(ifcContainer, ifcPath)
    # Close the document
    FreeCAD.closeDocument(newDocName)


def main():
    '''
    This function only wraps the argparser
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

    # Check the input step file path
    if not os.path.exists(args.step_fpath):
        raise Exception('Theres no file {}'.format(args.step_fpath))
    stepFpath = args.step_fpath
    ifcFpath = args.ifc_fpath
    convert_obj(stepFpath, ifcFpath)


if __name__ == '__main__':
    main()
