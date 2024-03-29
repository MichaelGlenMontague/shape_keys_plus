import bpy

from .. import core
from .. import memory


class OBJECT_OT_skp_shape_key_add(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_add'
    bl_label = core.strings['operators.ShapeKeyAdd.bl_label']
    bl_description = core.strings['operators.ShapeKeyAdd.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.EnumProperty(
        items=(
            ('DEFAULT', "", ""),
            ('FROM_MIX', "", ""),
            ('FROM_MIX_SELECTED', "", ""),
            ('FOLDER', "", "")
        ),
        default='DEFAULT',
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        valid_types = {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}
        
        return obj and obj.mode != 'EDIT' and obj.type in valid_types
    
    def execute(self, context):
        obj = context.object
        active = getattr(obj.active_shape_key, 'name', None)
        hidden = core.utils.hide(obj)
        key = core.key.add(self.type)
        key_blocks = obj.data.shape_keys.key_blocks
        
        if active:
            tree = memory.tree()
            ancestry = tree.ancestry(active)
            
            if core.settings.shape_key_auto_parent:
                if core.key.is_folder(key_blocks[active]):
                    tree.transfer(key.name, active)
                    tree.move(key.name, core.settings.shape_key_parent_placement)
                else:
                    placement = core.settings.shape_key_add_placement
                    
                    tree.reinsert(key.name, active)
                    
                    if placement == 'BOTTOM' or (placement == 'TOP' and (len(ancestry) > 1 or tree.locate(key.name)[1] > 1)):
                        tree.move(key.name, placement)
                    elif placement == 'BELOW':
                        tree.move(key.name, 'DOWN')
            else:
                placement = core.settings.shape_key_add_placement
                
                tree.reinsert(key.name, ancestry[1][0] if len(ancestry) > 1 else active)
                
                if placement == 'BOTTOM' or (placement == 'TOP' and tree.locate(key.name)[1] > 1):
                    tree.move(key.name, placement)
                elif placement == 'BELOW':
                    tree.move(key.name, 'DOWN')
            
            tree.apply()
        
        obj.active_shape_key_index = key_blocks.find(key.name)
        core.utils.show(hidden)
        
        return {'FINISHED'}
