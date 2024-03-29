import bpy

from .. import core


class DRIVER_OT_skp_variable_remove(bpy.types.Operator):
    bl_idname = 'driver.skp_variable_remove'
    bl_label = core.strings['operators.VariableRemove.bl_label']
    bl_description = core.strings['operators.VariableRemove.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        driver = core.key.get_driver(context.object.active_shape_key)
        
        if driver and len(driver.variables) > self.index:
            driver.variables.remove(driver.variables[self.index])
        
        return {'FINISHED'}
