import bpy

from .. import core
from .. import memory


class OBJECT_OT_skp_folder_ungroup(bpy.types.Operator):
    bl_idname = 'object.skp_folder_ungroup'
    bl_label = core.strings['operators.FolderUngroup.bl_label']
    bl_description = core.strings['operators.FolderUngroup.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data.shape_keys
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        folder = key_blocks[self.index]
        parents = memory.tree.active.get_parents(folder.name)
        active_name = obj.active_shape_key.name
        active_index = obj.active_shape_key_index
        
        if not core.key.is_folder(folder):
            return {'CANCELLED'}
        
        selections = core.key.deselect()
        
        if parents:
            # This folder's children are no longer being packed into 1 child of this folder's parent,
            # so this folder's parent has to have its children block value shifted upward by the number
            # of this folder's children. Then subtract 1 because the folder itself is also being removed.
            core.folder.shift_block_value(
                key_blocks[parents[0]], 'children', core.folder.get_block_value(folder, 'children') - 1)
        
        obj.active_shape_key_index = self.index
        bpy.ops.object.shape_key_remove()
        
        # Fix the active index.
        if active_index != self.index:
            obj.active_shape_key_index = key_blocks.find(active_name)
        
        core.key.reselect(selections)
        
        return {'FINISHED'}
