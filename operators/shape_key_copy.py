import bpy

from .. import core
from .. import memory


class OBJECT_OT_skp_shape_key_copy(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_copy'
    bl_label = core.strings['operators.ShapeKeyCopy.bl_label']
    bl_description = core.strings['operators.ShapeKeyCopy.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    mirror: bpy.props.IntProperty(options={'HIDDEN'})
    select: bpy.props.BoolProperty(options={'HIDDEN'})
    custom: bpy.props.BoolProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data.shape_keys and context.object.mode != 'EDIT'
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        hidden = core.utils.hide(obj)
        
        if self.select:
            selections = core.key.get_selected_indices()
            skip = []
            
            if not selections:
                return {'CANCELLED'}
            
            core.key.deselect()
            
            active_name = obj.active_shape_key.name
            selected_names = [key_blocks[i].name for i in selections]
            selected_copies = []
            
            for i in selections:
                if i in skip:
                    continue
                
                for key in [key_blocks[i]] + core.folder.get_children(key_blocks[i]):
                    index = key_blocks.find(key.name)
                    copy = core.key.copy(key, self.mirror, self.custom)
                    
                    if index in selections:
                        selected_copies.append(copy.name)
                        # Don't allow children to be copied multiple times.
                        # It may be useful sometimes, but it's not worth the hassle to implement properly.
                        if key != key_blocks[i]:
                            skip.append(index)
            
            tree = memory.tree()
            placement = core.settings.shape_key_add_placement
            
            for i in range(len(selected_copies))[::{'TOP': -1, 'BELOW': -1, 'BOTTOM': 1, 'ABOVE': 1}[placement]]:
                name = selected_names[i]
                copy = selected_copies[i]
                
                if key_blocks.find(name) in skip:
                    continue
                
                ancestry = tree.ancestry(name)
                
                if core.settings.shape_key_auto_parent:
                    tree.reinsert(copy, name)
                    
                    if placement == 'BOTTOM' or (placement == 'TOP' and (len(ancestry) > 1 or tree.locate(copy)[1] > 1)):
                        tree.move(copy, placement)
                    elif placement == 'BELOW':
                        tree.move(copy, 'DOWN')
                else:
                    tree.reinsert(copy, ancestry[1][0] if len(ancestry) > 1 else name)
                    
                    if placement == 'BOTTOM' or (placement == 'TOP' and tree.locate(copy)[1] > 1):
                        tree.move(copy, placement)
                    elif placement == 'BELOW':
                        tree.move(copy, 'DOWN')
            
            tree.apply()
            
            for name in selected_copies:
                core.key.select(name, True)
            
            obj.active_shape_key_index = key_blocks.find(active_name)
        else:
            active_key = obj.active_shape_key
            active_name = active_key.name
            active_copy = None
            
            for key in [active_key] + core.folder.get_children(active_key):
                copy = core.key.copy(key, self.mirror, self.custom)
                
                if not active_copy:
                    active_copy = copy.name
            
            tree = memory.tree()
            ancestry = tree.ancestry(active_name)
            placement = core.settings.shape_key_add_placement
            
            if core.settings.shape_key_auto_parent:
                tree.reinsert(active_copy, active_name)
                
                if placement == 'BOTTOM' or (placement == 'TOP' and (len(ancestry) > 1 or tree.locate(active_copy)[1] > 1)):
                    tree.move(active_copy, placement)
                elif placement == 'BELOW':
                    tree.move(active_copy, 'DOWN')
            else:
                tree.reinsert(active_copy, ancestry[1][0] if len(ancestry) > 1 else active_name)
                
                if placement == 'BOTTOM' or (placement == 'TOP' and tree.locate(active_copy)[1] > 1):
                    tree.move(active_copy, placement)
                elif placement == 'BELOW':
                    tree.move(active_copy, 'DOWN')
            
            tree.apply()
            
            obj.active_shape_key_index = key_blocks.find(active_copy)
        
        core.utils.show(hidden)
        
        return {'FINISHED'}
