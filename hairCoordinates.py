import bpy
import random
from mathutils import Vector

#check if two objects are a minimum distance apart
def checkDistance(object1, object2, minDistance):
    distVector = Vector(object1.location - object2.location)
    if(distVector.length >= minDistance):
        return True
    else:
        return False

#delete all objects of type EMPTY in the scene
def delete_all_empties():
    for obj in bpy.context.scene.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = obj.type == "EMPTY"
        bpy.ops.object.delete()

#main function to scatter objects on particle locations
def generate_biome(copy_objects, ps, minimum_distance):
    delete_all_empties()

    #this list should store all placed empties on an object
    list_all_my_empties = []

    ### Placement of empties starts here
    for p in ps.particles:
        bpy.ops.object.add(type='EMPTY', location=p.location)

        for currentEmpties in list_all_my_empties:
            # check if an object is currently selected and if any empties were created before
            if(len(bpy.context.selected_objects) > 0 and len(list_all_my_empties) > 0):
                if not checkDistance(bpy.context.selected_objects[0], currentEmpties, minimum_distance):
                    bpy.ops.object.delete()
            
        # if there is no currently selected object, then it was deleted
        # the first object should always be stored
        if(len(bpy.context.selected_objects) > 0):
            list_all_my_empties.append(bpy.context.selected_objects[0])

    ### Placement of objects starts here
    for empty in list_all_my_empties:
        #select random object from the list of objects
        copy_object = copy_objects[random.randint(0,len(copy_objects)-1)]
        #operations needed to create a copy of an object and place it
        new_tree = copy_object.copy()
        new_tree.data = copy_object.data.copy()
        new_tree.location = empty.location
        bpy.context.scene.objects.link(new_tree)
        
    ### Cleanup
    delete_all_empties()
    
############## MAIN #############

# given all the parameters below
# this can be turned into a function
# something like generate_biome(minimumDistance, copy_objects, particle_system):

### Parameters ###
minimum_distance = 2
copy_objects = [bpy.data.objects['Arbre Normal'], bpy.data.objects['Arbre Hiver'], bpy.data.objects['SapinHiver.015']]
ps = bpy.data.objects["Plane"].particle_systems["ParticleSystem"]
##################

generate_biome(copy_objects, ps, minimum_distance)