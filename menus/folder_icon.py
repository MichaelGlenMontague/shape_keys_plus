import bpy

from shape_keys_plus import core


def draw_menu(layout, context, category=None):
    operator = ('object.skp_active_folder_icon', 'object.skp_default_folder_icon')[context.area.type == 'PREFERENCES']
    
    if category:
        for i, p in enumerate(category):
            op = layout.operator(
                operator=operator,
                icon=p[0],
                text=p[2],
                translate=False)
            
            op.icons = p[-1]
            op.swap = False
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator=operator,
                icon=p[1],
                text=p[3],
                translate=False)
            
            if i < len(category) - 1:
                layout.separator(factor=0.5)
        
        return
    
    if context.area.type == 'PROPERTIES':
        selections = core.key.get_selected()
        
        if selections:
            layout.enabled = False
        
        obj = context.object
        active_key = obj.active_shape_key
        is_active_folder = active_key and core.key.is_folder(active_key)
        
        default_icon_pair = core.folder.get_icon_pair(core.preferences.default_folder_icon_pair)
        default_icon = default_icon_pair[core.preferences.default_folder_swap_icons]
        default_swapped_icon = default_icon_pair[not core.preferences.default_folder_swap_icons]
        
        if is_active_folder:
            icons_block = core.folder.get_block_value(active_key, 'icons')
            
            active_icon_pair = core.folder.get_icon_pair(icons_block)
            active_icon = active_icon_pair[icons_block < 0]
            active_swapped_icon = active_icon_pair[icons_block > 0]
            
            op = layout.operator(
                operator=operator,
                icon=default_icon,
                text=core.strings['menus.folder_icon.draw_menu.operator[%s (Default)]'] % default_icon_pair[2],
                translate=False)
            
            op.icons = 0
            op.swap = core.preferences.default_folder_swap_icons
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator=operator,
                icon=default_swapped_icon,
                text="")
            
            layout.separator(factor=0.5)
            
            op = layout.operator(
                operator=operator,
                icon=active_swapped_icon if icons_block != 0 else default_swapped_icon,
                text=core.strings['menus.folder_icon.draw_menu.operator[Swap (Active)]'],
                translate=False)
            
            if icons_block != 0:
                op.icons = abs(icons_block)
                op.swap = icons_block > 0
            else:
                op.icons = core.preferences.default_folder_icon_pair
                op.swap = not core.preferences.default_folder_swap_icons
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator=operator,
                icon=active_icon if icons_block != 0 else default_icon,
                text="")
            
            layout.separator(factor=0.5)
    
    layout.menu(
        menu='OBJECT_MT_skp_folder_icon_standard',
        text=core.strings['menus.folder_icon.draw_menu.menu[Standard]'],
        translate=False)
    
    layout.menu(
        menu='OBJECT_MT_skp_folder_icon_special',
        text=core.strings['menus.folder_icon.draw_menu.menu[Special]'],
        translate=False)
    
    layout.menu(
        menu='OBJECT_MT_skp_folder_icon_miscellaneous',
        text=core.strings['menus.folder_icon.draw_menu.menu[Miscellaneous]'],
        translate=False)


class OBJECT_MT_skp_folder_icon(bpy.types.Menu):
    bl_label = core.strings['menus.FolderIcon.bl_label']
    
    def draw(self, context):
        draw_menu(self.layout, context)


class OBJECT_MT_skp_folder_icon_standard(bpy.types.Menu):
    bl_label = core.strings['menus.FolderIcon.bl_label']
    
    def draw(self, context):
        draw_menu(self.layout, context, core.folder.icon_pairs_standard)


class OBJECT_MT_skp_folder_icon_special(bpy.types.Menu):
    bl_label = core.strings['menus.FolderIcon.bl_label']
    
    def draw(self, context):
        draw_menu(self.layout, context, core.folder.icon_pairs_special)


class OBJECT_MT_skp_folder_icon_miscellaneous(bpy.types.Menu):
    bl_label = core.strings['menus.FolderIcon.bl_label']
    
    def draw(self, context):
        draw_menu(self.layout, context, core.folder.icon_pairs_miscellaneous)
