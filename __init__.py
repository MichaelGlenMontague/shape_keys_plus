import bpy
import bl_ui

from shape_keys_plus import core
from shape_keys_plus import memory
from shape_keys_plus import operators
from shape_keys_plus import menus
from shape_keys_plus import panels
from shape_keys_plus import properties

bl_info = {
    "name": "Shape Keys+",
    "author": "Michael Glen Montague",
    "version": (2, 0, 0),
    "blender": (2, 83, 0),
    "location": "Properties > Object Data > Shape Keys+",
    "description": "Adds a panel with extra options for creating, sorting, viewing, and driving shape keys.",
    "warning": "",
    "wiki_url": "https://github.com/MichaelGlenMontague/shape_keys_plus/wiki",
    "tracker_url": "https://github.com/MichaelGlenMontague/shape_keys_plus/issues",
    "category": "Object"
}

# bl_info is parsed before the add-on is loaded, so its translations have to be copied by hand or a script.

bl_info_en_US = {
    "name": "Shape Keys+",
    "author": "Michael Glen Montague",
    "version": (2, 0, 0),
    "blender": (2, 83, 0),
    "location": "Properties > Object Data > Shape Keys+",
    "description": "Adds a panel with extra options for creating, sorting, viewing, and driving shape keys.",
    "warning": "",
    "wiki_url": "https://github.com/MichaelGlenMontague/shape_keys_plus/wiki",
    "tracker_url": "https://github.com/MichaelGlenMontague/shape_keys_plus/issues",
    "category": "Object"
}
bl_info_ja_JP = {
    "name": "シェイプキープラス (Shape Keys+)",
    "author": "Michael Glen Montague （マイケルグレンモンタギュー）",
    "version": (2, 0, 0),
    "blender": (2, 83, 0),
    "location": "プロパティ ⇒ オブジェクトデータ ⇒ シェイプキープラス",
    "description": "シェイプキーを作成したり整理したり見せたりドライブしたりのための余分設定を入っているパネルを追加します。",
    "warning": "",
    "wiki_url": "https://github.com/MichaelGlenMontague/shape_keys_plus/wiki",
    "tracker_url": "https://github.com/MichaelGlenMontague/shape_keys_plus/issues",
    "category": "Object"
}


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    def update_hide_default(self, context):
        if self.hide_default:
            bpy.utils.unregister_class(bl_ui.properties_data_mesh.DATA_PT_shape_keys)
        else:
            bpy.utils.register_class(bl_ui.properties_data_mesh.DATA_PT_shape_keys)
    
    def update_shape_key_icon(self, context):
        enum_items = bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items
        self.shape_key_icon_page = enum_items.find(self.shape_key_icon) // 10 + 1
    
    hide_default: bpy.props.BoolProperty(
        name=core.strings['AddonPreferences.hide_default.name'],
        description=core.strings['AddonPreferences.hide_default.description'],
        default=True,
        update=update_hide_default)
    
    default_folder_icon_pair: bpy.props.IntProperty(
        name=core.strings['AddonPreferences.default_folder_icon_pair.name'],
        min=1,
        max=core.folder.icon_pairs[-1][-1],
        default=1)
    
    default_folder_swap_icons: bpy.props.BoolProperty(
        name=core.strings['AddonPreferences.default_folder_swap_icons.name'],
        default=False)
    
    shape_key_icon: bpy.props.EnumProperty(
        items=[
            (ei.identifier, ei.name, ei.description, ei.icon, ei.value) for
            ei in bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items],
        default='NONE',
        update=update_shape_key_icon)
    
    shape_key_icon_page: bpy.props.IntProperty(
        min=1,
        max=len(range(0, len(bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items), 10)),
        default=1)
    
    def draw(self, context):
        layout = self.layout
        icon_pair = core.folder.get_icon_pair(self.default_folder_icon_pair)
        
        row = layout.row()
        row.alignment = 'RIGHT'
        
        row.prop(
            data=self,
            property='hide_default',
            translate=False)
        
        row = layout.row()
        row.alignment = 'RIGHT'
        box = row.box()
        box.alignment = 'LEFT'
        box.label(
            text=core.strings['AddonPreferences.draw.label[Default Folder Icon]'],
            translate=False)
        
        box.menu(
            menu='OBJECT_MT_skp_folder_icon',
            text=icon_pair[2])
        
        box = box.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(icon=icon_pair[self.default_folder_swap_icons])
        
        row.prop(
            data=self,
            property='default_folder_swap_icons',
            text="",
            icon='ARROW_LEFTRIGHT')
        
        row.label(icon=icon_pair[not self.default_folder_swap_icons])
        
        row = layout.row()
        row.alignment = 'RIGHT'
        box = row.box()
        box.alignment = 'CENTER'
        row = box.row(align=True)
        
        col = row.column()
        col.alignment = 'LEFT'
        col.label(
            text=core.strings['AddonPreferences.draw.label[Shape Key Icon]'],
            translate=False)
        
        col = row.column()
        col.popover(
            panel='DATA_PT_skp_shape_key_icon',
            text="",
            icon=self.shape_key_icon if self.shape_key_icon != 'NONE' else 'BLANK1')


class MESH_UL_shape_keys_plus(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0, flt_flag=0):
        obj = active_data
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        tree = memory.tree.active
        
        if not tree:
            # The active tree hasn't been created yet, for some reason.
            # Hopefully it will exist on the next call.
            return
        
        ancestry = tree.get_ancestry(item.name)
        
        selections = [key.name for key in core.key.get_selected()]
        selected = item.name in selections
        is_folder = core.key.is_folder(item)
        parents = [p[0] for p in ancestry[1:]]
        parent_selected = bool([p for p in parents if p in selections])
        
        use_edit_mode = obj.use_shape_key_edit_mode and obj.type == 'MESH'
        
        frame = layout.row(align=True)
        frame.active = not selections or selected
        
        # Check if this shape key belongs to a folder.
        if parents:
            # Get the number of folders this shape key is stacked in.
            for _ in range(len(ancestry) - 1):
                # Use the customizable folder indentation.
                for _ in range(core.settings.shape_key_indent_scale):
                    frame.separator(factor=1)
        
        if is_folder:
            op = frame.operator(
                operator='object.skp_folder_toggle',
                text="",
                icon=core.folder.get_active_icon(item),
                emboss=False)

            op.index = index
            
            frame.prop(
                data=item,
                property='name',
                text="",
                emboss=False)
        else:
            frame.prop(
                data=item,
                property='name',
                text="",
                emboss=False,
                icon=core.preferences.shape_key_icon)
        
        buttons = layout.row(align=True)
        buttons.alignment = 'RIGHT'
        
        if (item.mute and not selected) or (obj.mode == 'EDIT' and not use_edit_mode):
            buttons.active = False
        
        if selections and not selected:
            buttons.active = False
        
        if is_folder:
            op = buttons.operator(
                operator='object.skp_folder_ungroup',
                text="",
                icon='X',
                emboss=False)

            op.index = index
        else:
            if not item.id_data.use_relative:
                buttons.prop(
                    data=item,
                    property='frame',
                    text="",
                    emboss=False)
            elif index > 0:
                vrow = buttons.row()
                vrow.active = not selections or selections and selected
                vrow.scale_x = 0.66
                vrow.prop(
                    data=item,
                    property='value',
                    text="",
                    emboss=False)
            
            buttons.prop(
                data=item,
                property='mute',
                text="",
                icon='HIDE_OFF',
                emboss=False)
        
        if index > 0:
            if selected:
                icon = 'CHECKBOX_HLT'
            elif parent_selected:
                icon = 'SNAP_FACE_CENTER'
            else:
                icon = 'CHECKBOX_DEHLT'
            
            op = buttons.operator(
                operator='object.skp_shape_key_select',
                text="",
                icon=icon,
                emboss=False)
            
            op.index = index
            op.mode = 'TOGGLE'
    
    def draw_filter(self, context, layout):
        row = layout.row()
        
        subrow = row.row(align=True)
        
        subrow.prop(
            data=self,
            property='filter_name',
            text="")
        
        icon = 'ZOOM_OUT' if self.use_filter_invert else 'ZOOM_IN'
        
        subrow.prop(
            data=self,
            property='use_filter_invert',
            text="",
            icon=icon)
        
        icon = 'FILE_FOLDER'
        
        subrow.prop(
            data=core.settings,
            property='show_filtered_folder_contents',
            text="",
            icon=icon)
        
        subrow = row.row(align=True)
        
        icon = 'HIDE_OFF'
        
        subrow.prop(
            data=core.settings,
            property='shape_key_limit_to_active',
            text="",
            icon=icon)
        
        if core.settings.shape_key_limit_to_active:
            subrow.prop(
                data=core.settings,
                property='filter_active_threshold',
                text="")
            
            icon = 'TRIA_LEFT' if core.settings.filter_active_below else 'TRIA_RIGHT'
            
            subrow.prop(
                data=core.settings,
                property='filter_active_below',
                text="",
                icon=icon)
    
    def filter_items(self, context, data, propname):
        flt_flags = []
        flt_name_flags = []
        flt_neworder = []
        
        key_blocks = data.key_blocks
        helper_funcs = bpy.types.UI_UL_list
        filtering_by_name = False
        name_filters = [False] * len(key_blocks)
        
        memory.changed()
        
        tree = memory.tree.active
        
        def filter_set(i, f):
            # self.bitflag_filter_item allows a shape key to be shown.
            # 0 will prevent a shape key from being shown.
            flt_flags[i] = self.bitflag_filter_item if f else 0
        
        def filter_get(i):
            return flt_flags[i] is not 0
        
        if self.filter_name:
            filtering_by_name = True
            
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name,
                self.bitflag_filter_item, key_blocks, 'name')

            for i in range(len(flt_flags)):
                if flt_flags[i] == self.bitflag_filter_item:
                    name_filters[i] = True
        else:
            # Initialize every shape key as visible.
            flt_flags = [self.bitflag_filter_item] * len(key_blocks)
        
        for idx, key in enumerate(key_blocks):
            ancestry = tree.get_ancestry(key.name)
            location = tree.get_location(key.name)
            branch = core.utils.get(*location)
            
            children = branch[1:] if type(branch) == list and branch.index(key.name) == 0 else []
            parented = len(ancestry) > 1
            parents = [p[0] for p in ancestry[1:][::-1]]
            
            hidden = False
            
            if parented:
                parent_collapsed = False
                
                for p in parents:
                    if not core.folder.get_block_value(key_blocks[p], 'expand'):
                        parent_collapsed = True
                        break
                
                if parent_collapsed and not filtering_by_name:
                    hidden = True
            
            if hidden:
                filter_set(idx, False)
            
            if filtering_by_name and parented:
                for p in parents:
                    parent_index = key_blocks.find(p)
                    parent_hidden = not name_filters[parent_index]
                    
                    if name_filters[idx] and parent_hidden:
                        filter_set(parent_index, True)
            
            if core.settings.show_filtered_folder_contents:
                if children and filter_get(idx):
                    for i in range(len(children)):
                        filter_set(idx + 1 + i, True)
            
            if core.settings.shape_key_limit_to_active:
                if children:
                    filter_set(idx, False)
                else:
                    val = core.settings.filter_active_threshold
                    below = core.settings.filter_active_below
                    
                    in_active_range = \
                        key.value <= val if \
                        below else \
                        key.value >= val
                    
                    filter_set(idx, in_active_range)
        
        return flt_flags, flt_neworder


classes = (
    AddonPreferences,
    
    operators.DriverUpdate,
    operators.ActiveFolderIcon,
    operators.DefaultFolderIcon,
    operators.FolderMutate,
    operators.FolderToggle,
    operators.FolderUngroup,
    operators.ShapeKeyAdd,
    operators.ShapeKeyCopy,
    operators.ShapeKeyMirror,
    operators.ShapeKeyMove,
    operators.ShapeKeyParent,
    operators.ShapeKeyRemove,
    operators.ShapeKeySelect,
    operators.VariableAdd,
    operators.VariableCopy,
    operators.VariableMove,
    operators.VariableRemove,
    
    menus.ShapeKeyParent,
    menus.ShapeKeyParentSelected,
    menus.FolderIcon,
    menus.FolderIconStandard,
    menus.FolderIconSpecial,
    menus.FolderIconMiscellaneous,
    menus.ShapeKeyAddContextMenu,
    menus.ShapeKeyAddContextMenuSelected,
    menus.ShapeKeyCopyContextMenu,
    menus.ShapeKeyCopyContextMenuSelected,
    menus.ShapeKeyRemoveContextMenu,
    menus.ShapeKeyRemoveContextMenuSelected,
    menus.ShapeKeyOtherContextMenu,
    menus.ShapeKeyOtherContextMenuSelected,
    
    panels.ShapeKeysPlus,
    panels.ShapeKeyDriver,
    panels.ShapeKeyIcon,
    panels.CopyCustomization,
    
    properties.CopyCustomization,
    properties.KeyProperties,
    properties.SceneProperties,
    
    MESH_UL_shape_keys_plus
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.shape_keys_plus = bpy.props.PointerProperty(
        type=properties.SceneProperties, name=core.strings['Shape Keys+'])
    bpy.types.Key.shape_keys_plus = bpy.props.PointerProperty(
        type=properties.KeyProperties, name=core.strings['Shape Keys+'])
    
    core.preferences = bpy.context.preferences.addons['shape_keys_plus'].preferences
    
    default_panel_exists = hasattr(bpy.types, 'DATA_PT_shape_keys')
    
    if core.preferences.hide_default and default_panel_exists:
        bpy.utils.unregister_class(bl_ui.properties_data_mesh.DATA_PT_shape_keys)
    
    # Blender 2.79b, SKP v1.0.x
    if hasattr(bpy.types, 'OBJECT_PT_skp_shape_keys_plus'):
        bpy.utils.unregister_class(bpy.types.OBJECT_PT_skp_shape_keys_plus)
    
    # Blender 2.79b, SKP v1.1.x
    if hasattr(bpy.types, 'OBJECT_PT_shape_keys_plus'):
        bpy.utils.unregister_class(bpy.types.OBJECT_PT_shape_keys_plus)


def unregister():
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)
    
    default_panel_exists = hasattr(bpy.types, 'DATA_PT_shape_keys')
    
    if not default_panel_exists:
        bpy.utils.register_class(bl_ui.properties_data_mesh.DATA_PT_shape_keys)
