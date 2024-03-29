import bpy

from .. import core


class DATA_PT_skp_copy_customization(bpy.types.Panel):
    bl_label = core.strings['panels.CopyCustomization.bl_label']
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.data.shape_keys and context.object.mode != 'EDIT'
    
    def draw(self, context):
        if context.object.data.shape_keys:
            cc = context.object.data.shape_keys.shape_keys_plus.copy_customization
        else:
            cc = context.scene.shape_keys_plus.copy_customization
            self.layout.enabled = False
        
        flow = self.layout.column_flow(columns=2, align=True)
        bools = flow.column(align=True)
        props = flow.column(align=True)
        
        data_bool = bools.row(align=True)
        data_bool.active = cc.use_data
        data_bool.prop(
            data=cc,
            property='use_data',
            text=core.strings['properties.CopyCustomization.data.name'],
            translate=False,
            toggle=True)
        data_prop = props.row(align=True)
        data_prop.active = cc.use_data
        
        if context.object.data.shape_keys:
            data_prop.prop_search(
                data=cc,
                property='data',
                search_data=context.object.data.shape_keys,
                search_property='key_blocks',
                text="")
        else:
            data_prop.prop(data=cc, property='data', text="", icon='SHAPEKEY_DATA')
        
        relative_key_bool = bools.row(align=True)
        relative_key_bool.active = cc.use_relative_key
        relative_key_bool.prop(
            data=cc,
            property='use_relative_key',
            text=core.strings['panels.ShapeKeysPlus.draw.label[Relative To]'],
            translate=False,
            toggle=True)
        relative_key_prop = props.row(align=True)
        relative_key_prop.active = cc.use_relative_key
        
        if context.object.data.shape_keys:
            relative_key_prop.prop_search(
                data=cc,
                property='relative_key',
                search_data=context.object.data.shape_keys,
                search_property='key_blocks',
                text="")
        else:
            relative_key_prop.prop(data=cc, property='relative_key', text="", icon='SHAPEKEY_DATA')
        
        vertex_group_bool = bools.row(align=True)
        vertex_group_bool.active = cc.use_vertex_group
        vertex_group_bool.prop(
            data=cc,
            property='use_vertex_group',
            text=core.strings['properties.CopyCustomization.vertex_group.name'],
            translate=False,
            toggle=True)
        vertex_group_prop = props.row(align=True)
        vertex_group_prop.active = cc.use_vertex_group
        vertex_group_prop.prop_search(
            data=cc,
            property='vertex_group',
            search_data=context.object,
            search_property='vertex_groups',
            text="")
        
        mute_bool = bools.row(align=True)
        mute_bool.active = cc.use_mute
        mute_bool.prop(
            data=cc,
            property='use_mute',
            text=core.strings['properties.CopyCustomization.mute.name'],
            translate=False,
            toggle=True)
        mute_prop = props.row(align=True)
        mute_prop.active = cc.use_mute
        mute_prop.prop(
            data=cc,
            property='mute',
            text=core.strings[str(cc.mute)],
            translate=False,
            icon=('HIDE_OFF', 'HIDE_ON')[cc.mute],
            toggle=True)
        
        value_bool = bools.row(align=True)
        value_bool.active = cc.use_value
        value_bool.prop(
            data=cc,
            property='use_value',
            text=core.strings['properties.CopyCustomization.value.name'],
            translate=False,
            toggle=True)
        value_prop = props.row(align=True)
        value_prop.active = cc.use_value
        value_prop.prop(data=cc, property='value', text="")
        
        slider_min_bool = bools.row(align=True)
        slider_min_bool.active = cc.use_slider_min
        slider_min_bool.prop(
            data=cc,
            property='use_slider_min',
            text=core.strings['properties.CopyCustomization.slider_min.name'],
            translate=False,
            toggle=True)
        slider_min_prop = props.row(align=True)
        slider_min_prop.active = cc.use_slider_min
        slider_min_prop.prop(data=cc, property='slider_min', text="")
        
        slider_max_bool = bools.row(align=True)
        slider_max_bool.active = cc.use_slider_max
        slider_max_bool.prop(
            data=cc,
            property='use_slider_max',
            text=core.strings['properties.CopyCustomization.slider_max.name'],
            translate=False,
            toggle=True)
        slider_max_prop = props.row(align=True)
        slider_max_prop.active = cc.use_slider_max
        slider_max_prop.prop(data=cc, property='slider_max', text="")
        
        driver_bool = bools.row(align=True)
        driver_bool.active = cc.use_driver
        driver_bool.prop(
            data=cc,
            property='use_driver',
            text=core.strings['properties.CopyCustomization.driver.name'],
            translate=False,
            toggle=True)
        driver_prop = props.row(align=True)
        driver_prop.active = cc.use_driver
        
        interpolation_bool = bools.row(align=True)
        interpolation_bool.active = cc.use_interpolation
        interpolation_bool.prop(
            data=cc,
            property='use_interpolation',
            text=core.strings['properties.CopyCustomization.interpolation.name'],
            translate=False,
            toggle=True)
        interpolation_prop = props.row(align=True)
        interpolation_prop.active = cc.use_interpolation
        interpolation_prop.prop(data=cc, property='interpolation', text="")
        
        if context.object.data.shape_keys:
            driver_prop.prop_search(
                data=cc,
                property='driver',
                search_data=context.object.data.shape_keys,
                search_property='key_blocks',
                text="")
        else:
            driver_prop.prop(data=cc, property='driver', text="", icon='SHAPEKEY_DATA')
        
        mirror_row = self.layout.row(align=True)
        
        mirror_col = mirror_row.column(align=True)
        mirror_col.prop(
            data=cc,
            property='mirrored',
            text=core.strings['properties.CopyCustomization.mirrored.name'],
            translate=False,
            icon='PASTEFLIPDOWN',
            toggle=True)
        
        mirror_topology_col = mirror_row.column(align=True)
        mirror_topology_col.active = cc.mirrored
        mirror_topology_col.prop(
            data=cc,
            property='mirrored_topology',
            text=core.strings['properties.CopyCustomization.mirrored_topology.name'],
            translate=False,
            toggle=True)
        
        self.layout.separator(factor=0.5)
        
        op = self.layout.operator(
            operator='object.skp_shape_key_copy',
            text=core.strings[
                'panels.CopyCustomization.draw.operator[Copy' +
                ((', Mirrored' + ' (Topology)' * cc.mirrored_topology) * cc.mirrored) +
                ']'],
            translate=False,
            icon='PASTEDOWN' if not cc.mirrored else 'PASTEFLIPDOWN')
        
        op.mirror = (cc.mirrored + cc.mirrored_topology) * cc.mirrored
        op.select = bool(core.key.get_selected_indices())
        op.custom = True
