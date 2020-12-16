import bpy

from shape_keys_plus import core


class DRIVER_OT_skp_driver_update(bpy.types.Operator):
    bl_idname = 'driver.skp_driver_update'
    bl_label = core.strings['operators.DriverUpdate.bl_label']
    bl_description = core.strings['operators.DriverUpdate.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        core.driver.refresh(core.key.get_driver(context.object.active_shape_key))
        return {'FINISHED'}
