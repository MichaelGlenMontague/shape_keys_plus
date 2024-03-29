import bpy

from .. import core


class MESH_MT_skp_shape_key_copy_context_menu(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyCopyContextMenu.bl_label']
    
    def draw(self, context):
        layout = self.layout
        selections = core.key.get_selected()
        
        if selections:
            row = layout.row()
            
            row.menu(
                menu='MESH_MT_skp_shape_key_copy_context_menu_selected',
                text=core.strings['Selected (%s)'] % len(selections),
                translate=False,
                icon='CHECKBOX_HLT')
            
            layout.separator()
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_copy',
            text=core.strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored]'],
            translate=False,
            icon='PASTEFLIPDOWN')
        
        op.mirror = 1
        op.select = False
        op.custom = False
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_copy',
            text=core.strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored (Topology)]'],
            translate=False,
            icon='PASTEFLIPDOWN')
        
        op.mirror = 2
        op.select = False
        op.custom = False
        
        layout.separator(factor=0.5)
        
        row = layout.row()
        row.enabled = not selections
        
        if selections:
            row.operator(
                operator='object.skp_shape_key_copy',
                text=core.strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Customized]'],
                translate=False,
                icon='PRESET')
        else:
            row.popover(
                panel='DATA_PT_skp_copy_customization',
                text=core.strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Customized]'],
                translate=False,
                icon='PRESET')


class MESH_MT_skp_shape_key_copy_context_menu_selected(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyCopyContextMenu.bl_label']
    
    def draw(self, context):
        layout = self.layout
        
        op = layout.operator(
            operator='object.skp_shape_key_copy',
            text=core.strings['menus.ShapeKeyCopyContextMenuSelected.draw.operator[Copy Shape Key]'],
            translate=False,
            icon='PASTEDOWN')
        
        op.mirror = 0
        op.select = True
        op.custom = False
        
        op = layout.operator(
            operator='object.skp_shape_key_copy',
            text=core.strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored]'],
            translate=False,
            icon='PASTEFLIPDOWN')
        
        op.mirror = 1
        op.select = True
        op.custom = False
        
        op = layout.operator(
            operator='object.skp_shape_key_copy',
            text=core.strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored (Topology)]'],
            translate=False,
            icon='PASTEFLIPDOWN')
        
        op.mirror = 2
        op.select = True
        op.custom = False
        
        layout.separator(factor=0.5)
        
        layout.popover(
            panel='DATA_PT_skp_copy_customization',
            text=core.strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Customized]'],
            translate=False,
            icon='PRESET')
