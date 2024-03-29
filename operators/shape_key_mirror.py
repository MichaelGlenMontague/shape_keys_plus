import bpy

from .. import core
from .. import memory


class OBJECT_OT_skp_shape_key_mirror(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_mirror'
    bl_label = core.strings['operators.ShapeKeyMirror.bl_label']
    bl_description = core.strings['operators.ShapeKeyMirror.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    select: bpy.props.BoolProperty(options={'HIDDEN'})
    use_topology: bpy.props.BoolProperty(
        name=core.strings['operators.ShapeKeyMirror.use_topology.name'],
        description=core.strings['operators.ShapeKeyMirror.use_topology.description'],
        default=False)
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data.shape_keys and context.object.mode != 'EDIT'
    
    def execute(self, context):
        obj = context.object
        key_blocks = obj.data.shape_keys.key_blocks
        original_index = obj.active_shape_key_index
        
        buffer = set()
        
        if self.select:
            for key in core.key.get_selected():
                if core.key.is_folder(key):
                    for child in core.folder.get_children(key):
                        buffer.add(child.name)
                else:
                    buffer.add(key.name)
        else:
            if core.key.is_folder(obj.active_shape_key):
                for child in core.folder.get_children(obj.active_shape_key):
                    buffer.add(child.name)
            else:
                buffer.add(obj.active_shape_key.name)
        
        for name in buffer:
            key = key_blocks[name]
            obj.active_shape_key_index = key_blocks.find(name)
            bpy.ops.object.shape_key_mirror(use_topology=self.use_topology)
            
            if name.endswith(".L"):
                name = name[:-2] + ".R"
            elif name.endswith(".R"):
                name = name[:-2] + ".L"
            
            key.name = name
        
        obj.active_shape_key_index = original_index
        
        return {'FINISHED'}
