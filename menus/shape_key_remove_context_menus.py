import bpy

from .. import core


class MESH_MT_skp_shape_key_remove_context_menu(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyRemoveContextMenu.bl_label']
    
    def draw(self, context):
        layout = self.layout
        selections = core.key.get_selected()
        
        if selections:
            row = layout.row()
            
            row.menu(
                menu='MESH_MT_skp_shape_key_remove_context_menu_selected',
                text=core.strings['Selected (%s)'] % len(selections),
                translate=False,
                icon='CHECKBOX_HLT')
            
            layout.separator()
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_remove',
            text=core.strings['menus.ShapeKeyRemoveContextMenu.draw.operator[Delete All Shape Keys]'],
            translate=False,
            icon='X')
        
        op.type = 'CLEAR'


class MESH_MT_skp_shape_key_remove_context_menu_selected(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyRemoveContextMenu.bl_label']
    
    def draw(self, context):
        layout = self.layout
        
        op = layout.operator(
            operator='object.skp_shape_key_remove',
            icon='REMOVE',
            text=core.strings['menus.ShapeKeyRemoveContextMenuSelected.draw.operator[Remove Shape Key]'],
            translate=False)
        
        op.type = 'DEFAULT_SELECTED'
