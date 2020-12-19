import bpy

from shape_keys_plus import core


class OBJECT_OT_skp_shape_key_select(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_select'
    bl_label = core.strings['operators.ShapeKeySelect.bl_label']
    bl_description = core.strings['operators.ShapeKeySelect.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: bpy.props.EnumProperty(
        items=(
            ('TOGGLE', "", ""),
            ('ALL', "", ""),
            ('NONE', "", ""),
            ('INVERSE', "", "")
        ),
        options={'HIDDEN'})
    
    index: bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data.shape_keys
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        selections = shape_keys.shape_keys_plus.selections
        
        if self.mode == 'TOGGLE':
            core.key.select(self.index, str(self.index) not in selections)
        elif self.mode == 'ALL':
            for index, key in enumerate(key_blocks):
                if str(index) not in selections:
                    core.key.select(index, True)
        elif self.mode == 'NONE':
            selections.clear()
        elif self.mode == 'INVERSE':
            for index, key in enumerate(key_blocks):
                core.key.select(index, str(index) not in selections)
        
        return {'FINISHED'}
