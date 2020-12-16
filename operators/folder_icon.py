import bpy

from shape_keys_plus import core


class OBJECT_OT_skp_active_folder_icon(bpy.types.Operator):
    bl_idname = 'object.skp_active_folder_icon'
    bl_label = core.strings['operators.ActiveFolderIcon.bl_label']
    bl_description = core.strings['operators.ActiveFolderIcon.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    icons: bpy.props.IntProperty(
        min=0,
        max=core.folder.icon_pairs[-1][-1],
        options={'HIDDEN'})
    
    swap: bpy.props.BoolProperty(
        name=core.strings['operators.ActiveFolderIcon.swap.name'],
        default=False,
        options={'HIDDEN'})
    
    def execute(self, context):
        core.folder.set_block_value(context.object.active_shape_key, 'icons', self.icons * (1, -1)[self.swap])
        return {'FINISHED'}


class OBJECT_OT_skp_default_folder_icon(bpy.types.Operator):
    bl_idname = 'object.skp_default_folder_icon'
    bl_label = core.strings['operators.DefaultFolderIcon.bl_label']
    bl_description = core.strings['operators.DefaultFolderIcon.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    icons: bpy.props.IntProperty(
        min=1,
        max=core.folder.icon_pairs[-1][-1],
        options={'HIDDEN'})
    
    swap: bpy.props.BoolProperty(
        name=core.strings['operators.DefaultFolderIcon.swap.name'],
        default=False,
        options={'HIDDEN'})
    
    def execute(self, context):
        core.preferences.default_folder_icon_pair = self.icons
        core.preferences.default_folder_swap_icons = self.swap
        
        return {'FINISHED'}