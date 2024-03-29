import bpy

from .. import core
from .. import memory


class OBJECT_OT_skp_shape_key_move(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_move'
    bl_label = core.strings['operators.ShapeKeyMove.bl_label']
    bl_description = core.strings['operators.ShapeKeyMove.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.EnumProperty(
        name='Type',
        items=(
            ('TOP', core.strings['operators.ShapeKeyMove.type.items[TOP].name'], ""),
            ('UP', core.strings['operators.ShapeKeyMove.type.items[UP].name'], ""),
            ('DOWN', core.strings['operators.ShapeKeyMove.type.items[DOWN].name'], ""),
            ('BOTTOM', core.strings['operators.ShapeKeyMove.type.items[BOTTOM].name'], ""),
        ))
    
    selected: bpy.props.BoolProperty(
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        
        if not obj or obj.mode == 'EDIT':
            return False
        
        if core.key.get_selected():
            return True
        
        if obj.active_shape_key:
            return len(memory.tree.active.get_family(obj.active_shape_key.name)) > 1
        else:
            return False
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        hidden = core.utils.hide(obj)
        original_name = obj.active_shape_key.name
        original_index = obj.active_shape_key_index
        
        tree = memory.tree()
        
        if self.selected:
            selections = core.key.deselect()
            
            if self.type in ('DOWN', 'TOP'):
                selections = selections[::-1]
            
            for name in selections:
                tree.move(name, self.type)
            
            tree.apply()
            
            core.key.reselect(selections)
        else:
            tree.move(original_name, self.type)
            tree.apply()
        
        original_index = key_blocks.find(original_name)
        obj.active_shape_key_index = original_index
        
        core.utils.show(hidden)
        
        return {'FINISHED'}
