import bpy

from .. import core


class MESH_MT_skp_shape_key_other_context_menu(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyOtherContextMenu.bl_label']
    
    def draw(self, context):
        layout = self.layout
        selections = core.key.get_selected()
        
        if selections:
            row = layout.row()
            
            row.menu(
                menu='MESH_MT_skp_shape_key_other_context_menu_selected',
                text=core.strings['Selected (%s)'] % len(selections),
                translate=False,
                icon='CHECKBOX_HLT')
            
            layout.separator()
        
        active_key = context.object.active_shape_key
        is_active_folder = active_key and core.key.is_folder(active_key)
        
        if active_key:
            row = layout.row()
            row.enabled = not selections
            
            row.menu(
                menu='OBJECT_MT_skp_shape_key_parent',
                text=core.strings['menus.ShapeKeyOtherContextMenu.draw.menu[Set Parent...]'],
                translate=False,
                icon='FILE_PARENT')
        
        row = layout.row()
        row.enabled = not selections
        
        if is_active_folder:
            row.menu(
                menu='OBJECT_MT_skp_folder_icon',
                icon='COLOR')
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_mirror',
            text=core.strings['menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key]'],
            translate=False,
            icon='ARROW_LEFTRIGHT')
        
        op.select = False
        op.use_topology = False
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_mirror',
            text=core.strings['menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key (Topology)]'],
            translate=False,
            icon='ARROW_LEFTRIGHT')
        
        op.select = False
        op.use_topology = True
        
        row = layout.row()
        row.enabled = not selections
        
        row.operator(
            operator='object.shape_key_transfer',
            icon='COPY_ID')
        
        row = layout.row()
        row.enabled = not selections
        
        row.operator(
            operator='object.join_shapes',
            icon='COPY_ID')


class MESH_MT_skp_shape_key_other_context_menu_selected(bpy.types.Menu):
    bl_label = core.strings['menus.ShapeKeyOtherContextMenu.bl_label']
    
    def draw(self, context):
        layout = self.layout
        
        layout.menu(
            menu='OBJECT_MT_skp_shape_key_parent_selected',
            text=core.strings['menus.ShapeKeyOtherContextMenu.draw.menu[Set Parent...]'],
            translate=False,
            icon='FILE_PARENT')
        
        op = layout.operator(
            operator='object.skp_shape_key_mirror',
            text=core.strings['menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key]'],
            translate=False,
            icon='ARROW_LEFTRIGHT')
        
        op.select = True
        op.use_topology = False
        
        op = layout.operator(
            operator='object.skp_shape_key_mirror',
            text=core.strings['menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key (Topology)]'],
            translate=False,
            icon='ARROW_LEFTRIGHT')
        
        op.select = True
        op.use_topology = True
