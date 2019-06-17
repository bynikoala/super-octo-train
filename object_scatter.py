bl_info = {
   "name": "Object Scatter Add-on",
   "author": "die gang",
   "blender": (2, 7, 9),
   "description": "scatter objects",
   "category": "Mesh"
}

import bpy

class ScatterObjects:
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

        if len(obj.particle_systems) == 0:
            obj.modifiers.new("part", type='PARTICLE_SYSTEM')
            part = obj.particle_systems[0]

            settings = part.settings
            settings.emit_from = 'FACE'
            settings.physics_type = 'NO'
            settings.particle_size = 0.01
            settings.render_type = 'OBJECT'
            settings.dupli_object = bpy.data.objects[obj_name]
            settings.show_unborn = True
            settings.use_dead = True
            settings.count = count

            bpy.ops.object.duplicates_make_real()

        bpy.ops.group.create(name="generated_objects")
        grp = bpy.data.groups.get("generated_objects")

        print(obj)

        for i in range(1, count + 1):
            count_string = ""
            if i >= 100:
                count_string = str(i)
            elif i >= 10:
                count_string = "0" + str(i)
            else:
                count_string = "00" + str(i)
            name = obj_name + "." + count_string
            generated_obj = bpy.data.objects[name]
            grp.objects.link(generated_obj)
            generated_obj.parent = obj
            generated_obj.matrix_parent_inverse = obj.matrix_world.inverted()

        print(obj.particle_systems[0].particles)
        for particle in obj.particle_systems[0].particles:
            print(particle.location)

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
