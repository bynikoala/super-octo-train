bl_info = {
   "name": "Object Scatter Add-on",
   "author": "die gang",
   "version": (1, 0, 0),
   "blender": (2, 7, 9),
   "description": "scatter objects",
   "category": "Mesh", 
   "location": "View 3d > Edit Mode > Mesh",
}

import bpy
import random
from mathutils import Vector

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )

class Settings(PropertyGroup):

    bpath = StringProperty(
        name="Basedir",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    minDist = IntProperty(
        name = "Minimum distance",
        description="Specify the minimum distance between objects",
        default = 2,
        min = 2,
        max = 10
        )

    biome = EnumProperty(
        name="Biome:",
        description="Apply Data to attribute.",
        items=[ ('desert', "Desert", ""),
                ('ice', "Ice", ""),
                ('forest', "Forest", ""),
               ]
        )

class ScatterObjectsPanel(Panel):
    bl_idname = "object.custom_panel"
    bl_label = "Scatter Objects"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "TOOLS"    
    bl_category = "Tools"

    @classmethod
    def poll(self,context):
        return context.object is not None

    # def draw_header(self, context):
    #     layout = self.layout
    #     layout.label(text="Scatter Objects", icon="PHYSICS")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "bpath")
        layout.prop(mytool, "biome", text="") 
        layout.prop(mytool, "minDist")

        layout.operator("mesh.scatter_objects", text='Scatter Objects', icon='EDITMODE_HLT')
        



class ScatterObjects(Operator):
    bl_idname = "mesh.scatter_objects"
    bl_label = "Scatter objects on selected mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene
        mytool = scene.my_tool

        original_obj = bpy.context.active_object
        biom = mytool.biome
        #get file; every model must follow the convention basepath\\'biomName'\\'biomName'_models.blend
        basepath = mytool.bpath # 'C:\\Users\\nikoala\\Desktop\\hfu\\DVmed\\Models\\'
        filepath = basepath + biom + '\\' + biom + '_models.blend'

        #append object from .blend file
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects

        #create new group
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.group.create(name="imported_objects")
        imp_grp = bpy.data.groups.get("imported_objects")


        #separate the the selected face from the rest of the mesh
        bpy.ops.object.mode_set(mode='EDIT')
        mesh_before_separation = [ob for ob in bpy.data.objects if ob.type == 'MESH']
        bpy.ops.mesh.separate(type='SELECTED')
        mesh_after_separation = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        #get the separated object
        for i in mesh_before_separation:
            mesh_after_separation.remove(i)    
        obj = mesh_after_separation[0]

        #add texture according to biom; bugs out if selection isn't in object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        ScatterObjects.addTexture(self, biom, basepath, obj)

        #put the imported objects into a group
        for imp_obj in data_to.objects:
            test_obj = imp_obj
            imp_grp.objects.link(imp_obj)
            bpy.context.scene.objects.link(imp_obj)

        bpy.ops.object.mode_set(mode='OBJECT')
        count = 20

        mesh_before_scattering = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        #add particle system
        if len(obj.particle_systems) == 0:
            obj.modifiers.new("part", type='PARTICLE_SYSTEM')
            part = obj.particle_systems[0]

            settings = part.settings
            settings.emit_from = 'FACE'
            settings.physics_type = 'NO'
            settings.particle_size = 1
            #settings.render_type = 'OBJECT'
            settings.dupli_object = test_obj
            settings.show_unborn = True
            settings.use_dead = True
            settings.count = count
            settings.type = 'HAIR'
            settings.hair_length = 0
            settings.count = 300
            
            bpy.ops.object.duplicates_make_real()


        ### scatter objects
        HairCoordinates.generate_biome(self,data_to.objects, obj.particle_systems[0], mytool.minDist)

        mesh_after_scattering = [ob for ob in bpy.data.objects if ob.type == 'MESH']
        bpy.ops.group.create(name="generated_objects")
        grp = bpy.data.groups.get("generated_objects")


        #get the scattered objects and put them into a group
        for i in mesh_before_scattering:
            mesh_after_scattering.remove(i)

        for generated_obj in mesh_after_scattering:
            grp.objects.link(generated_obj)
            generated_obj.parent = original_obj
            generated_obj.matrix_parent_inverse = obj.matrix_world.inverted()

        #remove the imported objects
        objs = bpy.data.objects
        for imp_obj in data_to.objects:
            objs.remove(imp_obj, do_unlink=True)

        #remove particle system
        obj.select = True
        obj.modifiers.remove(obj.modifiers.get("part"))

        #merge original obj and separated face together
        bpy.ops.object.select_all(action = "DESELECT")
        obj.select = True
        original_obj.select = True
        bpy.context.scene.objects.active = original_obj
        bpy.ops.object.join()
        return {'FINISHED'} 

    #add texture
    def addTexture(self, biom, basepath, obj):
        mat_name = biom + "_texture"
        #import jpg texture; must follow naming conventions
        image_path = basepath + biom + '\\' + mat_name + '.jpg'
        
        mat = (bpy.data.materials.get(mat_name) or
            bpy.data.materials.new(mat_name))

        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        #clear nodes and add new important ones
        nodes.clear()
        output  = nodes.new("ShaderNodeOutputMaterial")
        diffuse = nodes.new("ShaderNodeBsdfPrincipled")
        texture = nodes.new("ShaderNodeTexImage")

        texture.image = bpy.data.images.load(image_path)

        links.new(output.inputs['Surface'], diffuse.outputs['BSDF'])
        links.new(diffuse.inputs['Base Color'],   texture.outputs['Color'])

        #distribute nodes
        for index, node in enumerate((texture, diffuse, output)):
            node.location.x = 200.0 * index
            
        #unwrap and add material
        obj.select = True
        bpy.context.scene.objects.active = obj
        for vertex in obj.data.vertices:
            vertex.select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.unwrap()

        obj.active_material = mat
        bpy.ops.object.mode_set(mode='OBJECT')

class HairCoordinates():
    #check if two objects are a minimum distance apart
    def checkDistance(self, object1, object2, minDistance):
        distVector = Vector(object1.location - object2.location)
        if(distVector.length >= minDistance):
            return True
        else:
            return False

    #delete all objects of type EMPTY in the scene
    def delete_all_empties(self):
        for obj in bpy.context.scene.objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = obj.type == "EMPTY"
            bpy.ops.object.delete()

    #main function to scatter objects on particle locations
    def generate_biome(self, copy_objects, ps, minimum_distance):
        
        bpy.ops.object.mode_set(mode='OBJECT')
        HairCoordinates.delete_all_empties(self)

        #this list should store all placed empties on an object
        list_all_my_empties = []

        ### Placement of empties starts here
        for p in ps.particles:
            bpy.ops.object.add(type='EMPTY', location=p.location)

            for currentEmpties in list_all_my_empties:
                # check if an object is currently selected and if any empties were created before
                if(len(bpy.context.selected_objects) > 0 and len(list_all_my_empties) > 0):
                    if not HairCoordinates.checkDistance(self, bpy.context.selected_objects[0], currentEmpties, minimum_distance):
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
        HairCoordinates.delete_all_empties(self)
        
    ############## MAIN #############

    # given all the parameters below
    # this can be turned into a function
    # something like generate_biome(minimumDistance, copy_objects, particle_system):

    ### Parameters ###
    #minimum_distance = 2
    #copy_objects = [bpy.data.objects['Arbre Normal'], bpy.data.objects['Arbre Hiver'], bpy.data.objects['SapinHiver.015']]
    #ps = bpy.data.objects["Plane"].particle_systems["ParticleSystem"]
    ##################

    #generate_biome(copy_objects, ps, minimum_distance)

classes = (
    Settings,
    ScatterObjects,
    ScatterObjectsPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=Settings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()

# def register():
#     bpy.utils.register_module(__name__)
#     bpy.types.Scene.my_tool = bpy.types.PointerProperty(type=Settings)
#     #bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)


# def unregister():
#     bpy.utils.unregister_module(__name__)
#     del bpy.types.Scene.my_tool

# if __name__ == "__main__":
#     register()