# Export STEP to IFC in FreeCAD

When working with simple single parts file, this process is seamless.
But when doing it in a assembly, specially a very nested assembly, this
is a little complicated.

First, you need to change the options in FreeCAD to import the STEP assembly
as a *"assembly per document"*. Then one will have the correct tree strucuture.

If you just export the model to IFC, then the only item exported will be the
top element, and there will be no shape. 
It makes sense, since the top element is just a conglomerate of individual
pieces.

**Use the ifc++ to visualize the ifc models and tree info**

`
# To get the children of the obj
obj.OutList
# To check the item type
# 'App::Part' assembly
# 'Part::Feature' part
obj.TypeId
# Create a ifc container
obj1 = Arch.makeBuildingPart()
# Set a placement of a object based on anothers
obj.Placement = obj1.Placement.copy()
# Sets the label(the name on the tree)
obj1.Label = "NewName"
# Create a new BIM component
obj = Arch.makeComponent(FreeCAD.ActiveDocument.<Name of the document>)
# Import object
import ImportGui
ImportGui.insert(u"<path_to_file>", "TreeName")
# This will happen once one enable the multipart STEP import
App.getDocument("<TreeName>").saveAs("<path_to_file.FCStd">)
# Exporting to IFC
__objs__ = []
__objs__.append(FreeCAD.ActiveDocument.getObject("<container_tree_name>"))
import exportIFC
exportIFC.export(__objs__, u"<path_to_ifc.ifc>")
# Open new document
App.newDocument("<name>")
# Change the IFC type
FreeCAD.ActiveDocument.getObject("<object_name>") = u"<ifc_type>"
`

# Finding the container with most child

`
# Get all the container objects in the tree
containers = list(filter(lambda x: x.TypeId == 'App::Part', FreeCAD.ActiveDocument.Objects))
# Gets the children count
childrenCount = [len(x.OutListRecursive) for x in containers]
# Sort them
sortedList = [x for _, x in sorted(zip(childrenCount, containers), key=lambda duo: duo[0])]
# The main container
mainContainer = sortedList[-1]
`