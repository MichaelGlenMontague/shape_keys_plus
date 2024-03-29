import bpy

from .. import core
from .. import memory


class OBJECT_OT_skp_folder_toggle(bpy.types.Operator):
    bl_idname = 'object.skp_folder_toggle'
    bl_label = core.strings['operators.FolderToggle.bl_label']
    bl_description = core.strings['operators.FolderToggle.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data.shape_keys
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        active_key = obj.active_shape_key
        
        if active_key and key_blocks[self.index].name in memory.tree.active.get_parents(active_key.name):
            # The active index shouldn't be on a hidden shape key.
            obj.active_shape_key_index = self.index
        
        core.folder.toggle(key_blocks[self.index])
        
        return {'FINISHED'}
