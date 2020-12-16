import bpy

from shape_keys_plus import core


class DRIVER_OT_skp_variable_add(bpy.types.Operator):
    bl_idname = 'driver.skp_variable_add'
    bl_label = core.strings['operators.VariableAdd.bl_label']
    bl_description = core.strings['operators.VariableAdd.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        driver = core.key.get_driver(context.object.active_shape_key)
        
        if driver:
            driver.variables.new()
        
        return {'FINISHED'}
