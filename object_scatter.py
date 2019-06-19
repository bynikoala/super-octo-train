bl_info = {
   "name": "Object Scatter Add-on",
   "author": "die gang",
   "blender": (2, 7, 9),
   "description": "scatter objects",
   "category": "Mesh"
}

import bpy

class ScatterObjects(bpy.types.Operator):

    bl_idname = "mesh.scatter_objects"
    bl_label = "Scatter objects on selected mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.wm.append(directory = 'C:\\Users\\Robin\\Documents\\code\\python_workspace\\blender-DvinMp\\cartoon_lowpoly_trees_blend.blend\\Object\\', filename='Tree_1')

        bpy.ops.object.mode_set(mode='EDIT')
        mesh_before_separation = [ob for ob in bpy.data.objects if ob.type == 'MESH']
        bpy.ops.mesh.separate(type='SELECTED')
        mesh_after_separation = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        for i in mesh_before_separation:
            mesh_after_separation.remove(i)
            
        obj = mesh_after_separation[0]

        bpy.ops.object.mode_set(mode='OBJECT')
        count = 20
        obj_name = 'Tree_1'

        mesh_before_scattering = [ob for ob in bpy.data.objects if ob.type == 'MESH']

        if len(obj.particle_systems) == 0:
            obj.modifiers.new("part", type='PARTICLE_SYSTEM')
            part = obj.particle_systems[0]

            settings = part.settings
            settings.emit_from = 'FACE'
            settings.physics_type = 'NO'
            settings.particle_size = 0.02
            settings.render_type = 'OBJECT'
            settings.dupli_object = bpy.data.objects[obj_name]
            settings.show_unborn = True
            settings.use_dead = True
            settings.count = count

            bpy.ops.object.duplicates_make_real()
    
        mesh_after_scattering = [ob for ob in bpy.data.objects if ob.type == 'MESH']
        bpy.ops.group.create(name="generated_objects")
        grp = bpy.data.groups.get("generated_objects")

        for i in mesh_before_scattering:
            mesh_after_scattering.remove(i)
            
        for generated_obj in mesh_after_scattering:
            grp.objects.link(generated_obj)
            generated_obj.parent = obj
            generated_obj.matrix_parent_inverse = obj.matrix_world.inverted()

        objs = bpy.data.objects
        objs.remove(objs[obj_name], do_unlink=True)
        obj.select = True
        obj.modifiers.remove(obj.modifiers.get("part"))


def register():
    print("Register Object Scatter")
    bpy.utils.register_class(ScatterObjects)

def unregister():
    print("Unregister Object Scatter")
    bpy.utils.unregister_class(ScatterObjects)

if __name__ == "__main__":
    register()