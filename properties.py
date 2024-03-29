import bpy

from . import core


class CopyCustomization(bpy.types.PropertyGroup):
    def get_slider_min(self):
        return self.get('slider_min', 0.0)
    
    def set_slider_min(self, v):
        self['slider_min'] = max(-10.000, min(v, self.get('slider_max', 1.0) - 0.001))
    
    def get_slider_max(self):
        return self.get('slider_max', 1.0)
    
    def set_slider_max(self, v):
        self['slider_max'] = max(self.get('slider_min', 0.0) + 0.001, min(v, 10.000))
    
    def get_value(self):
        return self.get('value', 0.0)
    
    def set_value(self, v):
        self['value'] = max(self.get('slider_min', 0.0), min(v, self.get('slider_max', 1.0)))
    
    use_data: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_data.name'])
    use_slider_min: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_slider_min.name'])
    use_slider_max: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_slider_max.name'])
    use_value: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_value.name'])
    use_vertex_group: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_vertex_group.name'])
    use_relative_key: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_relative_key.name'])
    use_interpolation: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_interpolation.name'])
    use_mute: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_mute.name'])
    use_driver: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.use_driver.name'])
    
    data: bpy.props.StringProperty(name=core.strings['properties.CopyCustomization.data.name'])
    
    slider_min: bpy.props.FloatProperty(
        name=core.strings['properties.CopyCustomization.slider_min.name'],
        precision=3,
        default=0.0,
        get=get_slider_min,
        set=set_slider_min)
    
    slider_max: bpy.props.FloatProperty(
        name=core.strings['properties.CopyCustomization.slider_max.name'],
        precision=3,
        default=1.0,
        get=get_slider_max,
        set=set_slider_max)
    
    value: bpy.props.FloatProperty(
        name=core.strings['properties.CopyCustomization.value.name'],
        precision=3,
        default=0.0,
        get=get_value,
        set=set_value)
    
    vertex_group: bpy.props.StringProperty(name=core.strings['properties.CopyCustomization.vertex_group.name'])
    
    relative_key: bpy.props.StringProperty(name=core.strings['properties.CopyCustomization.relative_key.name'])
    
    interpolation: bpy.props.EnumProperty(
        name=core.strings['properties.CopyCustomization.interpolation.name'],
        description=bpy.types.ShapeKey.bl_rna.properties['interpolation'].description,
        items=[
            (ei.identifier, ei.name, ei.description, ei.icon, ei.value) for
            ei in bpy.types.ShapeKey.bl_rna.properties['interpolation'].enum_items
        ],
        default=bpy.types.ShapeKey.bl_rna.properties['interpolation'].default)
    
    mute: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.mute.name'])
    
    driver: bpy.props.StringProperty(name=core.strings['properties.CopyCustomization.driver.name'])
    
    mirrored: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.mirrored.name'])
    mirrored_topology: bpy.props.BoolProperty(name=core.strings['properties.CopyCustomization.mirrored_topology.name'])


class KeyProperties(bpy.types.PropertyGroup):
    selections: bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup,
        name=core.strings['Selections'])
    
    copy_customization: bpy.props.PointerProperty(
        type=CopyCustomization,
        name=core.strings['properties.KeyProperties.copy_customization.name'])


class SceneProperties(bpy.types.PropertyGroup):
    shape_key_add_placement: bpy.props.EnumProperty(
        name=core.strings['properties.SceneProperties.shape_key_add_placement.name'],
        items=(
            ('TOP', core.strings['properties.SceneProperties.shape_key_add_placement.items[TOP].name'],
             core.strings['properties.SceneProperties.shape_key_add_placement.items[TOP].description'],
             'TRIA_UP_BAR', 0),
            ('ABOVE', core.strings['properties.SceneProperties.shape_key_add_placement.items[ABOVE].name'],
             core.strings['properties.SceneProperties.shape_key_add_placement.items[ABOVE].description'],
             'TRIA_UP', 1),
            ('BELOW', core.strings['properties.SceneProperties.shape_key_add_placement.items[BELOW].name'],
             core.strings['properties.SceneProperties.shape_key_add_placement.items[BELOW].description'],
             'TRIA_DOWN', 2),
            ('BOTTOM', core.strings['properties.SceneProperties.shape_key_add_placement.items[BOTTOM].name'],
             core.strings['properties.SceneProperties.shape_key_add_placement.items[BOTTOM].description'],
             'TRIA_DOWN_BAR', 3)
        ),
        default='BELOW')
    
    shape_key_parent_placement: bpy.props.EnumProperty(
        name=core.strings['properties.SceneProperties.shape_key_parent_placement.name'],
        items=(
            ('TOP', core.strings['properties.SceneProperties.shape_key_parent_placement.items[TOP].name'],
             core.strings['properties.SceneProperties.shape_key_parent_placement.items[TOP].description'],
             'TRIA_UP_BAR', 0),
            ('BOTTOM', core.strings['properties.SceneProperties.shape_key_parent_placement.items[BOTTOM].name'],
             core.strings['properties.SceneProperties.shape_key_parent_placement.items[BOTTOM].description'],
             'TRIA_DOWN_BAR', 1)
        ),
        default='BOTTOM')
    
    shape_key_unparent_placement: bpy.props.EnumProperty(
        name=core.strings['properties.SceneProperties.shape_key_unparent_placement.name'],
        items=(
            ('TOP', core.strings['properties.SceneProperties.shape_key_unparent_placement.items[TOP].name'],
             core.strings['properties.SceneProperties.shape_key_unparent_placement.items[TOP].description'],
             'TRIA_UP_BAR', 0),
            ('ABOVE', core.strings['properties.SceneProperties.shape_key_unparent_placement.items[ABOVE].name'],
             core.strings['properties.SceneProperties.shape_key_unparent_placement.items[ABOVE].description'],
             'TRIA_UP', 1),
            ('BELOW', core.strings['properties.SceneProperties.shape_key_unparent_placement.items[BELOW].name'],
             core.strings['properties.SceneProperties.shape_key_unparent_placement.items[BELOW].description'],
             'TRIA_DOWN', 2),
            ('BOTTOM', core.strings['properties.SceneProperties.shape_key_unparent_placement.items[BOTTOM].name'],
             core.strings['properties.SceneProperties.shape_key_unparent_placement.items[BOTTOM].description'],
             'TRIA_DOWN_BAR', 3)
        ),
        default='ABOVE')
    
    shape_key_auto_parent: bpy.props.BoolProperty(
        name=core.strings['properties.SceneProperties.shape_key_auto_parent.name'],
        description=core.strings['properties.SceneProperties.shape_key_auto_parent.description'],
        default=True)
    
    shape_key_indent_scale: bpy.props.IntProperty(
        name=core.strings['properties.SceneProperties.shape_key_indent_scale.name'],
        description=core.strings['properties.SceneProperties.shape_key_indent_scale.description'],
        min=0,
        max=6,
        default=3)
    
    show_filtered_folder_contents: bpy.props.BoolProperty(
        name=core.strings['properties.SceneProperties.show_filtered_folder_contents.name'],
        description=core.strings['properties.SceneProperties.show_filtered_folder_contents.description'],
        default=True)
    
    shape_key_limit_to_active: bpy.props.BoolProperty(
        name=core.strings['properties.SceneProperties.shape_key_limit_to_active.name'],
        description=core.strings['properties.SceneProperties.shape_key_limit_to_active.description'],
        default=False)
    
    filter_active_threshold: bpy.props.FloatProperty(
        name=core.strings['properties.SceneProperties.filter_active_threshold.name'],
        description=core.strings['properties.SceneProperties.filter_active_threshold.description'],
        soft_min=0.0,
        soft_max=1.0,
        default=0.001,
        step=1,
        precision=3)
    
    filter_active_below: bpy.props.BoolProperty(
        name=core.strings['properties.SceneProperties.filter_active_below.name'],
        description=core.strings['properties.SceneProperties.filter_active_below.description'],
        default=False)
    
    # Default `copy_customization` for when no Key is available.
    copy_customization: bpy.props.PointerProperty(
        type=CopyCustomization,
        name=core.strings['properties.KeyProperties.copy_customization.name'])
