import bpy

from shape_keys_plus import core


class DATA_PT_skp_shape_key_icon(bpy.types.Panel):
    bl_label = "Shape Key Icon"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    
    def draw(self, context):
        enum_items = bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items[:]
        page = core.preferences.shape_key_icon_page
        
        row = self.layout.row()
        row.alignment = 'CENTER'
        row.prop(
            data=core.preferences,
            property='shape_key_icon_page',
            text=core.strings['Page'],
            translate=False)
        
        row.label(text="of " + str(len(range(0, len(enum_items), 10))), translate=False)
        
        for ei in enum_items[(page - 1) * 10:(page - 1) * 10 + 10]:
            self.layout.prop_enum(
                data=core.preferences,
                property='shape_key_icon',
                value=ei.identifier,
                icon=ei.identifier if ei.identifier != 'NONE' else 'BLANK1')
        
        self.layout.prop_search(
            data=core.preferences,
            property='shape_key_icon',
            search_data=bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'],
            search_property='enum_items',
            text="",
            icon='BLANK1')
