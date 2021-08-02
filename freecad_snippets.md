# FreeCAD snippets

A simple file containing some snippets that I found useful.

- To get the children of the obj:
`obj.OutList`
- To check the item type: 
`obj.TypeId`
    - 'App::Part': Assembly
    - 'Part::Feature': Part/single component
- Create an ifc container: 
`obj = Arch.makeBuildingPart()`
- Set a placement of a object based on anothers: 
`obj.Placement = obj1.getGlobalPlacement()`
- Sets the label(the name on the tree): 
`obj1.Label = "NewName"`
- Create a new BIM component: 
`obj = Arch.makeComponent(FreeCAD.ActiveDocument.<Name of the document>)`
- Import object: 
```python
import ImportGui
ImportGui.insert(u"<path_to_file>", "TreeName")
# One need to save in order to use the multicomponent import
# For this to happen one have to enable this in the preferences
App.getDocument("<TreeName>").saveAs("<path_to_file.FCStd">)
```
- Exporting to IFC:
```python
# Create the list
__objs__ = []
# Collect the objects
__objs__.append(FreeCAD.ActiveDocument.getObject("<container_tree_name>"))
# Export the objects
import exportIFC
exportIFC.export(__objs__, u"<path_to_ifc.ifc>")
```
- Open new document:
`App.newDocument("<name>")`
- Change the IFC type: 
`FreeCAD.ActiveDocument.getObject("<object_name>") = u"<ifc_type>"`
- Change the workbench: 
`Gui.activateWorkbench("ArchWorkbench")`

- Finding the container with most child
```python
# Get all the container objects in the tree
containers = list(filter(lambda x: x.TypeId == 'App::Part', FreeCAD.ActiveDocument.Objects))
# Gets the children count
childrenCount = [len(x.OutListRecursive) for x in containers]
# Sort them
sortedList = [x for _, x in sorted(zip(childrenCount, containers), key=lambda duo: duo[0])]
# The main container
mainContainer = sortedList[-1]
```