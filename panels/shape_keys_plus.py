import bpy

from shape_keys_plus import core
from shape_keys_plus import memory


class DATA_PT_shape_keys_plus(bpy.types.Panel):
    bl_label = core.strings['Shape Keys+']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        valid_types = {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}
        
        return obj and obj.type in valid_types
    
    def draw(self, context):
        layout = self.layout
        
        core.settings = context.scene.shape_keys_plus
        
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        active_index = obj.active_shape_key_index
        selections = core.key.get_selected()
        
        is_active_folder = active_key and core.key.is_folder(active_key)
        
        enable_edit = obj.mode != 'EDIT'
        enable_edit_value = False
        
        if obj.show_only_shape_key is False:
            use_edit_mode = obj.type == 'MESH' and obj.use_shape_key_edit_mode
            
            if enable_edit or use_edit_mode:
                enable_edit_value = True
        
        header = layout.row()
        
        placement_box = header.box()
        col = placement_box.column()
        col.label(
            text=core.strings['panels.ShapeKeysPlus.draw.label[Placement]'],
            translate=False,
            icon='NLA_PUSHDOWN')
        
        col.separator()
        
        prop_data = core.settings.bl_rna.properties['shape_key_add_placement']
        
        col.prop_menu_enum(
            data=core.settings,
            property='shape_key_add_placement',
            text=core.strings['panels.ShapeKeysPlus.draw.prop_menu_enum[Add / Copy]'],
            translate=False,
            icon=prop_data.enum_items[core.settings.shape_key_add_placement].icon)
        
        prop_data = core.settings.bl_rna.properties['shape_key_parent_placement']
        
        col.prop_menu_enum(
            data=core.settings,
            property='shape_key_parent_placement',
            text=core.strings['panels.ShapeKeysPlus.draw.prop_menu_enum[Parent]'],
            translate=False,
            icon=prop_data.enum_items[core.settings.shape_key_parent_placement].icon)
        
        prop_data = core.settings.bl_rna.properties['shape_key_unparent_placement']
        
        col.prop_menu_enum(
            data=core.settings,
            property='shape_key_unparent_placement',
            text=core.strings['panels.ShapeKeysPlus.draw.prop_menu_enum[Unparent]'],
            translate=False,
            icon=prop_data.enum_items[core.settings.shape_key_unparent_placement].icon)
        
        hierarchy_box = header.box()
        col = hierarchy_box.column()
        col.label(
            text=core.strings['panels.ShapeKeysPlus.draw.label[Hierarchy]'],
            translate=False,
            icon='OUTLINER')
        
        col.separator()
        
        col.prop(
            data=core.settings,
            property='shape_key_auto_parent',
            icon='FILE_PARENT',
            toggle=True)
        
        col.prop(
            data=core.settings,
            property='shape_key_indent_scale',
            slider=True)
        
        selection_box = header.box()
        selection_box.scale_x = 0.75
        col = selection_box.column()
        
        if selections:
            col.label(
                text=core.strings['panels.ShapeKeysPlus.draw.label[%s Selected]'] % str(len(selections)),
                translate=False)
        else:
            col.label(
                text=core.strings['panels.ShapeKeysPlus.draw.label[Select...]'],
                translate=False,
                icon='RESTRICT_SELECT_OFF')
        
        col.separator()
        
        op = col.operator(
            operator='object.skp_shape_key_select',
            text=core.strings['panels.ShapeKeysPlus.draw.operator[Select All]'],
            translate=False,
            icon='ADD')
        
        op.mode = 'ALL'
        
        op = col.operator(
            operator='object.skp_shape_key_select',
            text=core.strings['panels.ShapeKeysPlus.draw.operator[Select None]'],
            translate=False,
            icon='REMOVE')
        
        op.mode = 'NONE'
        
        op = col.operator(
            operator='object.skp_shape_key_select',
            text=core.strings['panels.ShapeKeysPlus.draw.operator[Select Inverse]'],
            translate=False,
            icon='ARROW_LEFTRIGHT')
        
        op.mode = 'INVERSE'
        
        row = layout.row()
        
        row.template_list(
            listtype_name='MESH_UL_shape_keys_plus',
            dataptr=shape_keys,
            propname='key_blocks',
            active_dataptr=obj,
            active_propname='active_shape_key_index',
            list_id='SHAPE_KEYS_PLUS',
            rows=8 if active_key else 4)
        
        col = row.column(align=True)
        
        #####################
        ######## ADD ########
        #####################
        
        row = col.row(align=True)
        
        if selections:
            row.menu(
                menu='MESH_MT_skp_shape_key_add_context_menu',
                icon='ADD',
                text="")
        else:
            op = row.operator_menu_hold(
                operator='object.skp_shape_key_add',
                icon='ADD',
                text="",
                menu='MESH_MT_skp_shape_key_add_context_menu')
            
            op.type = 'DEFAULT'
        
        ######################
        ######## COPY ########
        ######################
        
        row = col.row(align=True)
        
        if selections:
            row.menu(
                menu='MESH_MT_skp_shape_key_copy_context_menu',
                icon='PASTEDOWN',
                text="")
        else:
            op = row.operator_menu_hold(
                operator='object.skp_shape_key_copy',
                icon='PASTEDOWN',
                text="",
                menu='MESH_MT_skp_shape_key_copy_context_menu')
            
            op.mirror = 0
            op.select = False
            op.custom = False
        
        ########################
        ######## REMOVE ########
        ########################
        
        row = col.row(align=True)
        
        if selections:
            row.menu(
                menu='MESH_MT_skp_shape_key_remove_context_menu',
                icon='REMOVE',
                text="")
        else:
            op = row.operator_menu_hold(
                operator='object.skp_shape_key_remove',
                icon='REMOVE',
                text="",
                menu='MESH_MT_skp_shape_key_remove_context_menu')
            
            op.type = 'DEFAULT'
        
        #######################
        ######## OTHER ########
        #######################
        
        col.separator()
        
        row = col.row()
        
        row.menu(
            menu='MESH_MT_skp_shape_key_other_context_menu',
            icon='DOWNARROW_HLT',
            text="")
        
        if not active_key:
            return
        
        col.separator()
        
        loc = memory.tree.active.get_location(active_key.name)
        
        sub = col.column(align=True)
        row = sub.row(align=True)
        row.enabled = bool(selections) or loc[1] > bool(memory.tree.active.get_parents(active_key.name))
        op = row.operator(
            operator='object.skp_shape_key_move',
            icon='TRIA_UP_BAR',
            text="")
        
        op.type = 'TOP'
        op.selected = bool(selections)
        
        op = sub.operator(
            operator='object.skp_shape_key_move',
            icon='TRIA_UP',
            text="")
        
        op.type = 'UP'
        op.selected = bool(selections)
        
        op = sub.operator(
            operator='object.skp_shape_key_move',
            icon='TRIA_DOWN',
            text="")
        
        op.type = 'DOWN'
        op.selected = bool(selections)
        
        row = sub.row(align=True)
        row.enabled = bool(selections) or loc[1] < len(loc[0]) - 1
        op = row.operator(
            operator='object.skp_shape_key_move',
            icon='TRIA_DOWN_BAR',
            text="")
        
        op.type = 'BOTTOM'
        op.selected = bool(selections)
        
        split = layout.split(factor=0.5, align=False)
        
        row = split.row()
        row.enabled = enable_edit
        
        row.prop(
            data=shape_keys,
            property='use_relative')
        
        row = split.row()
        row.alignment = 'RIGHT'
        
        sub = row.row(align=True).row(align=True)
        sub.active = enable_edit_value
        
        sub.prop(
            data=obj,
            property='show_only_shape_key',
            text="")
        
        sub.prop(
            data=obj,
            property='use_shape_key_edit_mode',
            text="")
        
        sub = row.row()
        
        if shape_keys.use_relative:
            sub.operator(
                operator='object.shape_key_clear',
                icon='X',
                text="")
        else:
            sub.operator(
                operator='object.shape_key_retime',
                icon='RECOVER_LAST',
                text="")
        
        if is_active_folder:
            return
        
        if shape_keys.use_relative:
            if active_index != 0:
                row = layout.row()
                row.active = enable_edit_value
                
                row.prop(
                    data=active_key,
                    property='value')
                
                split = layout.split()
                
                col = split.column(align=True)
                col.active = enable_edit_value
                
                col.label(
                    text=core.strings['panels.ShapeKeysPlus.draw.label[Range]'],
                    translate=False)
                
                col.prop(
                    data=active_key,
                    property='slider_min',
                    text=core.strings['panels.ShapeKeysPlus.draw.label[Range Min]'],
                    translate=False)
                
                col.prop(
                    data=active_key,
                    property='slider_max',
                    text=core.strings['panels.ShapeKeysPlus.draw.label[Range Max]'],
                    translate=False)
                
                col = split.column(align=True)
                col.active = enable_edit_value
                
                col.label(
                    text=core.strings['panels.ShapeKeysPlus.draw.label[Relative To]'],
                    translate=False)
                
                col.prop_search(
                    data=active_key,
                    property='vertex_group',
                    search_data=obj,
                    search_property='vertex_groups',
                    text="")
                
                col.prop_search(
                    data=active_key,
                    property='relative_key',
                    search_data=shape_keys,
                    search_property='key_blocks',
                    text="")
        else:
            layout.prop(
                data=active_key,
                property='interpolation')
            
            row = layout.column()
            row.active = enable_edit_value
            
            row.prop(
                data=shape_keys,
                property='eval_time')
