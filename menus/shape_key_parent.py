import bpy

from shape_keys_plus import core
from shape_keys_plus import memory


class OBJECT_MT_skp_shape_key_parent(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyParent.bl_label']
    
    def draw(self, context):
        layout = self.layout
        
        if core.key.get_selected_indices():
            layout.enabled = False
        
        active_key = context.object.active_shape_key
        
        if active_key:
            key_blocks = active_key.id_data.key_blocks
            parents = memory.tree.active.get_parents(active_key.name)
            parent = core.utils.get(parents, 0, "")
            grandparent = core.utils.get(parents, 1, "")
            
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text=core.strings['menus.ShapeKeyParent.draw.operator[New Folder]'],
                translate=False,
                icon='NEWFOLDER')
            
            op.type = 'NEW'
            op.child = active_key.name
            op.parent = parent
            
            if parent:
                layout.separator()
                
                op = layout.operator(
                    operator='object.skp_shape_key_parent',
                    text=core.strings['menus.ShapeKeyParent.draw.operator[Unparent from "%s"]'] % parent,
                    translate=False,
                    icon='X')
                
                op.type = 'UNPARENT'
                op.child = active_key.name
                op.parent = parent
            
            if grandparent:
                op = layout.operator(
                    operator='object.skp_shape_key_parent',
                    text=core.strings['menus.ShapeKeyParent.draw.operator[Unparent from "%s"]'] % parents[-1],
                    translate=False,
                    icon='CANCEL')
                
                op.type = 'CLEAR'
                op.child = active_key.name
                op.parent = parent
            
            # Only allow parenting to a folder that this shape key isn't already related to.
            children = core.folder.get_children(active_key)
            folders = [
                k for k in key_blocks if
                core.key.is_folder(k)
            ]
            
            if folders:
                layout.separator()
            
            for folder in folders:
                row = layout.row()
                
                if folder == active_key or folder.name == parent or folder in children:
                    row.enabled = False
                
                op = row.operator(
                    operator='object.skp_shape_key_parent',
                    text=("  " * len(memory.tree.active.get_parents(folder.name))) + folder.name,
                    translate=False,
                    icon=core.folder.get_active_icon(folder))
                
                op.type = 'PARENT'
                op.child = active_key.name
                op.parent = folder.name


class OBJECT_MT_skp_shape_key_parent_selected(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyParent.bl_label']
    
    def draw(self, context):
        layout = self.layout
        active_key = context.object.active_shape_key
        
        if active_key:
            key_blocks = active_key.id_data.key_blocks
            
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text=core.strings['menus.ShapeKeyParent.draw.operator[New Folder]'],
                translate=False,
                icon='NEWFOLDER')
            
            op.type = 'NEW_SELECTED'
            
            layout.separator()
            
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text=core.strings['menus.ShapeKeyParentSelected.draw.operator[Unparent from Parent]'],
                translate=False,
                icon='X')
            
            op.type = 'UNPARENT_SELECTED'
            
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text=core.strings['menus.ShapeKeyParentSelected.draw.operator[Unparent from Root]'],
                translate=False,
                icon='CANCEL')
            
            op.type = 'CLEAR_SELECTED'
            
            selections = [key.name for key in core.key.get_selected()]
            folders = [
                k for k in key_blocks if
                core.key.is_folder(k)
            ]
            
            if folders:
                layout.separator()
            
            for folder in folders:
                row = layout.row()
                
                parents = memory.tree.active.get_parents(folder.name)
                selected = folder.name in selections
                descendant = any(parent for parent in parents if parent in selections)
                
                if selected or descendant:
                    row.enabled = False
                
                op = row.operator(
                    operator='object.skp_shape_key_parent',
                    text=("  " * len(parents)) + folder.name,
                    translate=False,
                    icon=core.folder.get_active_icon(folder))
                
                op.type = 'PARENT_SELECTED'
                op.parent = folder.name
