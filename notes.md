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

By this moment, the best option is to use the python installatio present in the FreeCAD\bin.
In this way, all the modules are loaded. The UI has to be loaded to, in order to properly load all the methods.

Next steps:

- [ ] Make the freecad_step_to_ifc.py a cmd utilitie
- [ ] Add some loggin to the script
- [ ] Make the UI in electron
- [ ] Read the structure tree from FreeCAD and edit the IFC properties