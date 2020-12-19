import bpy

from shape_keys_plus import core
from shape_keys_plus import memory


def update(self, context):
    memory.changed()


class OBJECT_OT_skp_folder_mutate(bpy.types.Operator):
    bl_idname = 'object.skp_folder_mutate'
    bl_label = core.strings['operators.FolderMutate.bl_label']
    bl_description = core.strings['operators.FolderMutate.bl_description']
    bl_options = {'REGISTER', 'UNDO'}
    
    children: bpy.props.IntProperty(
        name=core.strings['operators.FolderMutate.children.name'],
        description=core.strings['operators.FolderMutate.children.description'],
        min=0,
        default=0,
        update=update)
    
    expand: bpy.props.BoolProperty(
        name=core.strings['operators.FolderMutate.expand.name'],
        description=core.strings['operators.FolderMutate.expand.description'],
        default=True)
    
    icons: bpy.props.IntProperty(
        name=core.strings['operators.FolderMutate.icons.name'],
        description=core.strings['operators.FolderMutate.icons.description'],
        min=-core.folder.icon_pairs[-1][-1],
        max=core.folder.icon_pairs[-1][-1],
        default=0)
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        obj = context.object
        active_key = obj.active_shape_key
        
        active_key.vertex_group = core.folder.generate(
            children=self.children,
            expand=int(self.expand),
            icons=self.icons)
        
        return {'FINISHED'}
