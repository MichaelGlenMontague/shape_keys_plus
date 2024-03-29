import bpy

from .. import core


class DRIVER_OT_skp_variable_copy(bpy.types.Operator):
    bl_idname = 'driver.skp_variable_copy'
    bl_label = core.strings['operators.VariableCopy.bl_label']
    bl_description = core.strings['operators.VariableCopy.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        driver = core.key.get_driver(context.object.active_shape_key)
        
        if driver and len(driver.variables) > self.index:
            var = driver.variables.new()
            vars = list(driver.variables)
            
            vars.insert(self.index + 1, vars.pop(len(vars) - 1))
            
            var.name = vars[self.index].name + "_copy"
            var.type = vars[self.index].type
            
            for t in range(len(vars[self.index].targets)):
                var.targets[t].bone_target = vars[self.index].targets[t].bone_target
                var.targets[t].data_path = vars[self.index].targets[t].data_path
                
                # Only the "Single Property" type can have its id_type changed.
                if var.type == 'SINGLE_PROP':
                    var.targets[t].id_type = vars[self.index].targets[t].id_type
                
                var.targets[t].id = vars[self.index].targets[t].id
                var.targets[t].transform_type = vars[self.index].targets[t].transform_type
                var.targets[t].rotation_mode = vars[self.index].targets[t].rotation_mode
                var.targets[t].transform_space = vars[self.index].targets[t].transform_space
            
            core.driver.reconstruct_variables(driver, vars)
        
        return {'FINISHED'}
