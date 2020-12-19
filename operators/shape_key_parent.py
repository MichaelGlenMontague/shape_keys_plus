import bpy

from shape_keys_plus import core
from shape_keys_plus import memory


class OBJECT_OT_skp_shape_key_parent(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_parent'
    bl_label = core.strings['operators.ShapeKeyParent.bl_label']
    bl_description = core.strings['operators.ShapeKeyParent.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.EnumProperty(
        items=(
            ('PARENT', "", core.strings['operators.ShapeKeyParent.type.items[PARENT].description']),
            ('UNPARENT', "", core.strings['operators.ShapeKeyParent.type.items[UNPARENT].description']),
            ('CLEAR', "", core.strings['operators.ShapeKeyParent.type.items[CLEAR].description']),
            ('NEW', "", core.strings['operators.ShapeKeyParent.type.items[NEW].description']),
            ('PARENT_SELECTED', "", core.strings['operators.ShapeKeyParent.type.items[PARENT_SELECTED].description']),
            ('UNPARENT_SELECTED', "", core.strings['operators.ShapeKeyParent.type.items[UNPARENT_SELECTED].description']),
            ('CLEAR_SELECTED', "", core.strings['operators.ShapeKeyParent.type.items[CLEAR_SELECTED].description']),
            ('NEW_SELECTED', "", core.strings['operators.ShapeKeyParent.type.items[NEW_SELECTED].description'])
        ),
        default='PARENT',
        options={'HIDDEN'})
    
    child: bpy.props.StringProperty(options={'HIDDEN'})
    parent: bpy.props.StringProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key and obj.active_shape_key_index >= 0 and obj.mode != 'EDIT'
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        active_key_name = obj.active_shape_key.name
        hidden = core.utils.hide(obj)
        selections = core.key.deselect()
        
        if self.type == 'PARENT':
            placement = core.settings.shape_key_parent_placement
            
            tree = memory.tree()
            tree.transfer(self.child, self.parent)
            tree.move(self.child, placement)
            tree.apply()
            
            # Highlight Original Key
            obj.active_shape_key_index = key_blocks.find(active_key_name)
            
            core.key.reselect(selections)
        elif self.type == 'UNPARENT':
            placement = core.settings.shape_key_unparent_placement
            
            tree = memory.tree()
            ancestry = tree.ancestry(self.child)
            
            if len(ancestry) > 1:
                tree.reinsert(self.child, ancestry[-1][0])
                
                if placement in ('TOP', 'BOTTOM'):
                    tree.move(self.child, placement)
                elif placement == 'BELOW':
                    tree.move(self.child, 'DOWN')
                
                tree.apply()
            
            # Highlight Original Key
            obj.active_shape_key_index = key_blocks.find(active_key_name)
            
            core.key.reselect(selections)
        elif self.type == 'CLEAR':
            placement = core.settings.shape_key_unparent_placement
            
            tree = memory.tree()
            ancestry = tree.ancestry(self.child)
            
            if len(ancestry) > 1:
                tree.reinsert(self.child, ancestry[1][0])
                
                if placement in ('TOP', 'BOTTOM'):
                    tree.move(self.child, placement)
                elif placement == 'BELOW':
                    tree.move(self.child, 'DOWN')
                
                tree.apply()
            
            # Highlight Original Key
            obj.active_shape_key_index = key_blocks.find(active_key_name)
            
            core.key.reselect(selections)
        elif self.type == 'NEW':
            # Here, the new key is being added as the parent to the active key.
            # The new key's own parenting works even when Auto Parent is turned off.
            active_key_name = obj.active_shape_key.name
            
            parent = core.key.add(type='FOLDER')
            
            tree = memory.tree()
            tree.reinsert(parent.name, active_key_name)
            tree.transfer(active_key_name, parent.name)
            tree.apply()
            
            # Highlight Original Key
            obj.active_shape_key_index = key_blocks.find(active_key_name)
            
            core.key.reselect(selections)
            
        elif self.type == 'PARENT_SELECTED':
            placement = core.settings.shape_key_parent_placement
            
            tree = memory.tree()
            
            for name in selections[::{'TOP': -1, 'BOTTOM': 1}[placement]]:
                tree.transfer(name, self.parent)
                tree.move(name, placement)
            
            tree.apply()
            
            # Highlight Original Key
            obj.active_shape_key_index = key_blocks.find(active_key_name)
            
            core.key.reselect(selections)
        elif self.type == 'UNPARENT_SELECTED':
            placement = core.settings.shape_key_unparent_placement
            
            tree = memory.tree()
            outward = sorted(core.utils.flatten(selections), key=lambda name: -len(tree.ancestry(name)))
            
            for name in outward[::{'TOP': -1, 'BELOW': -1, 'BOTTOM': 1, 'ABOVE': 1}[placement]]:
                ancestry = tree.ancestry(name)
                
                if len(ancestry) > 1:
                    tree.reinsert(name, ancestry[-1][0])
                    
                    if placement in ('TOP', 'BOTTOM'):
                        tree.move(name, placement)
                    elif placement == 'BELOW' and len(ancestry) > 1:
                        tree.move(name, 'DOWN')
            
            tree.apply()
            
            # Highlight Original Key
            obj.active_shape_key_index = key_blocks.find(active_key_name)
            
            core.key.reselect(selections)
        elif self.type == 'CLEAR_SELECTED':
            placement = core.settings.shape_key_unparent_placement
            
            tree = memory.tree()
            
            for name in selections[::{'TOP': -1, 'BELOW': -1, 'BOTTOM': 1, 'ABOVE': 1}[placement]]:
                ancestry = tree.ancestry(name)
                
                if len(ancestry) > 1:
                    tree.reinsert(name, ancestry[1][0])
                
                if placement in ('TOP', 'BOTTOM'):
                    tree.move(name, placement)
                elif placement == 'BELOW' and len(ancestry) > 1:
                    tree.move(name, 'DOWN')
            
            tree.apply()
            
            # Highlight Original Key
            obj.active_shape_key_index = key_blocks.find(active_key_name)
            
            core.key.reselect(selections)
        elif self.type == 'NEW_SELECTED':
            tree = memory.tree()
            
            # Here, the new key is being added as the parent to the selected key(s).
            # The new key's own parenting works even when Auto Parent is turned off.
            active_key_name = obj.active_shape_key.name
            
            # The oldest selected parent of the active key. If this exists, the new
            # folder will have to be created above it, instead of above the active key.
            selected_parents_descending = [p[0] for p in tree.ancestry(active_key_name)[::-1] if p[0] in selections]
            
            parent = core.key.add(type='FOLDER')
            
            tree = memory.tree()
            tree.reinsert(parent.name, core.utils.get(selected_parents_descending, 0, active_key_name))
            
            for name in selections:
                tree.transfer(name, parent.name)
            
            tree.apply()
            
            # Highlight Parent Folder
            obj.active_shape_key_index = key_blocks.find(parent.name)
            
            # Select (Only) Parent Folder
            core.key.select(parent, True)
        
        core.utils.show(hidden)
        
        return {'FINISHED'}
