'''
This is a macro to transform the selected STEP obj to a IFC, 
with the same tree structure and geometries.
'''
#TODO Check the workbench
#TODO Auto select obj
#TODO Change the name of the original object before the new
#TODO Automatic export
#TODO Change the IFC type
#TODO Add the headless functionality
#TODO Checks the properties for the IFC

def add_children(obj, container):
	# Check the type of obj
	if obj.TypeId == 'App::Part': # Assembly
		# Get the children
		children = obj.OutList
		for child in children:
			# Check the type
			if child.TypeId == 'App::Part': # Assembly
				# Create the container
				subCont = make_b_part(child)
				# Adds the child to the dad
				container.addObject(subCont)
				if len(child.OutList) != 0:
					add_children(child, subCont)
			elif child.TypeId == 'Part::Feature': # Part/Component
				# Make the component
				component = make_component(child)
				# Adds to its parent
				#COMM
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

# Get all the container objects in the tree
containers = list(filter(lambda x: x.TypeId == 'App::Part', FreeCAD.ActiveDocument.Objects))
# Gets the children count
childrenCount = [len(x.OutListRecursive) for x in containers]
# Sort them
sortedList = [x for _, x in sorted(zip(childrenCount, containers), key=lambda duo: duo[0])]
# The main container
obj = sortedList[-1]
step_to_ifc(obj)
	