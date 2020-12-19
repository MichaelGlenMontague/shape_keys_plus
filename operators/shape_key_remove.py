import bpy

from shape_keys_plus import core
from shape_keys_plus import memory


class OBJECT_OT_skp_shape_key_remove(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_remove'
    bl_label = core.strings['operators.ShapeKeyRemove.bl_label']
    bl_description = core.strings['operators.ShapeKeyRemove.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.EnumProperty(
        items=(
            ('DEFAULT', "", ""),
            ('CLEAR', "", ""),
            ('DEFAULT_SELECTED', "", "")
        ),
        default='DEFAULT',
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object.mode != 'EDIT' and context.object.data.shape_keys
    
    def execute(self, context):
        obj = bpy.context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        anim = shape_keys.animation_data
        
        if self.type == 'CLEAR':
            bpy.ops.object.shape_key_remove(all=True)
        elif self.type == 'DEFAULT':
            tree = memory.tree()
            ancestry = tree.ancestry(obj.active_shape_key.name)
            location = tree.locate(obj.active_shape_key.name, ancestry[-1])
            
            if len(ancestry) > 1:
                core.folder.shift_block_value(key_blocks[ancestry[-1][0]], 'children', -1)
            
            active_key = obj.active_shape_key
            obj.active_shape_key_index += core.folder.get_capacity(active_key)
            
            for key in reversed([active_key] + core.folder.get_children(active_key)):
                # Remove the driver first.
                if anim and anim.drivers:
                    for fc in anim.drivers:
                        if fc.data_path == "key_blocks[\"%s\"].value" % key.name:
                            anim.drivers.remove(fc)
                
                bpy.ops.object.shape_key_remove()
            
            if obj.data.shape_keys:
                if obj.active_shape_key.name == key_blocks[0].name and len(key_blocks) > 1:
                    # Don't let the reference key be automatically highlighted unless it's the only key left.
                    obj.active_shape_key_index = 1
                if len(location[0]) > 2:
                    if location[1] == 1:
                        # Don't let the parent key be automatically highlighted unless there are no more family members.
                        if type(location[0][2]) == list:
                            obj.active_shape_key_index = key_blocks.find(location[0][2][0])
                        else:
                            obj.active_shape_key_index = key_blocks.find(location[0][2])
                    else:
                        # Ensure that it's the previous sibling that's selected, not just the previous key.
                        if type(location[0][location[1] - 1]) == list:
                            obj.active_shape_key_index = key_blocks.find(location[0][location[1] - 1][0])
                        else:
                            obj.active_shape_key_index = key_blocks.find(location[0][location[1] - 1])
        elif self.type == 'DEFAULT_SELECTED':
            selections = core.key.deselect()
            
            for name in selections:
                index = key_blocks.find(name)
                
                if index == -1:
                    continue

                obj.active_shape_key_index = key_blocks.find(name) + core.folder.get_capacity(key_blocks[name])
                
                for key in reversed([key_blocks[index]] + core.folder.get_children(key_blocks[index])):
                    # Remove the driver first.
                    if anim and anim.drivers:
                        for fc in anim.drivers:
                            if fc.data_path == "key_blocks[\"%s\"].value" % key.name:
                                anim.drivers.remove(fc)
                    
                    bpy.ops.object.shape_key_remove()
        
        return {'FINISHED'}
