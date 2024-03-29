import bpy

from .. import core


class DRIVER_OT_skp_variable_move(bpy.types.Operator):
    bl_idname = 'driver.skp_variable_move'
    bl_label = core.strings['operators.VariableMove.bl_label']
    bl_description = core.strings['operators.VariableMove.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(options={'HIDDEN'})
    
    type: bpy.props.EnumProperty(
        items=(
            ('TOP', "", ""),
            ('UP', "", ""),
            ('DOWN', "", ""),
            ('BOTTOM', "", "")
        ),
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        driver = core.key.get_driver(context.object.active_shape_key)
        
        if driver and len(driver.variables) > self.index:
            vars = list(driver.variables)
            
            if self.type == 'TOP':
                vars.insert(0, vars.pop(self.index))
            elif self.type == 'UP' and self.index > 0:
                vars.insert(self.index - 1, vars.pop(self.index))
            elif self.type == 'DOWN' and self.index < len(vars) - 1:
                vars.insert(self.index + 1, vars.pop(self.index))
            elif self.type == 'BOTTOM':
                vars.insert(len(vars) - 1, vars.pop(self.index))
            
            core.driver.reconstruct_variables(driver, vars)
        
        return {'FINISHED'}
