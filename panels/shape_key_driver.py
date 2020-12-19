import bpy

from shape_keys_plus import core


class DATA_PT_skp_shape_key_driver(bpy.types.Panel):
    bl_label = core.strings['Driver']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id = 'DATA_PT_shape_keys_plus'
    bl_context = 'data'
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        valid_types = {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}
        
        if not (obj and obj.type in valid_types):
            return False
        
        shape_keys = obj.data.shape_keys
        
        if not shape_keys:
            return False
        
        key_blocks = shape_keys.key_blocks
        key = obj.active_shape_key
        
        return key and not core.key.is_folder(key) and key.name != key_blocks[0].name and core.key.get_driver(key)
    
    def draw(self, context):
        layout = self.layout
        
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        driver = core.key.get_driver(active_key)
        
        row = layout.row()
        row.label(text=core.strings['Type'] + ":", translate=False)
        
        row = row.row()
        row.prop(
            data=driver,
            property='type',
            text="")
        
        row.scale_x = 2
        
        if driver.type == 'SCRIPTED':
            row = row.row()
            row.prop(
                data=driver,
                property='use_self')
        
        if driver.type == 'SCRIPTED':
            row = layout.row()
            row.label(text=core.strings['Expression'] + ":", translate=False)
            
            row = row.row()
            row.prop(
                data=driver,
                property='expression',
                text="")
            
            row.scale_x = 4
        
        row = layout.row(align=True)
        
        row.operator(
            operator='driver.skp_variable_add',
            icon='ADD',
            text=core.strings['panels.ShapeKeyDriver.draw.operator[Add Variable]'],
            translate=False)
        
        row.operator(
            operator='driver.skp_driver_update',
            icon='FILE_REFRESH',
            text=core.strings['panels.ShapeKeyDriver.draw.operator[Update Driver]'],
            translate=False)
        
        for i, v in enumerate(driver.variables):
            area_parent = layout.row()
            area = area_parent.column(align=True)
            box = area.box()
            box2 = area_parent.box()
            row = box.row()
            
            op = row.operator(
                operator='driver.skp_variable_remove',
                icon='X',
                text="",
                emboss=False)
            
            op.index = i
            
            row.prop(
                data=driver.variables[i],
                property='name',
                text="")
            
            row = row.row()
            
            row.prop(
                data=driver.variables[i],
                property='type',
                text="")
            
            row.scale_x = 2
            
            row2 = box2.column(align=False)
            
            op_copy = row2.operator(
                operator='driver.skp_variable_copy',
                text="",
                icon='PASTEDOWN')
            
            op_copy.index = i
            
            row3 = box2.column(align=True)
            
            op_move_top = row3.operator(
                operator='driver.skp_variable_move',
                text="",
                icon='TRIA_UP_BAR')
            
            op_move_top.index = i
            op_move_top.type = 'TOP'
            
            op_move_up = row3.operator(
                operator='driver.skp_variable_move',
                text="",
                icon='TRIA_UP')
            
            op_move_up.index = i
            op_move_up.type = 'UP'
            
            op_move_down = row3.operator(
                operator='driver.skp_variable_move',
                text="",
                icon='TRIA_DOWN')
            
            op_move_down.index = i
            op_move_down.type = 'DOWN'
            
            op_move_bottom = row3.operator(
                operator='driver.skp_variable_move',
                text="",
                icon='TRIA_DOWN_BAR')
            
            op_move_bottom.index = i
            op_move_bottom.type = 'BOTTOM'
            
            if driver.variables[i].type == 'SINGLE_PROP':
                row = box.row(align=True)
                row.prop(
                    data=driver.variables[i].targets[0],
                    property='id_type',
                    icon_only=True)
                
                row.prop(
                    data=driver.variables[i].targets[0],
                    property='id',
                    text="")
                
                if driver.variables[i].targets[0].id:
                    row = box.row(align=True)
                    row.prop(
                        data=driver.variables[i].targets[0],
                        property='data_path',
                        text="",
                        icon='RNA')
            elif driver.variables[i].type == 'TRANSFORMS':
                target = driver.variables[i].targets[0]
                
                col = box.column(align=True)
                col.prop(
                    data=target,
                    property='id',
                    text=core.strings['Object'],
                    translate=False,
                    expand=True)
                
                if target and target.id and target.id.type == 'ARMATURE':
                    col.prop_search(
                        data=target,
                        property='bone_target',
                        search_data=target.id.data,
                        search_property='bones',
                        text=core.strings['Bone'],
                        translate=False,
                        icon='BONE_DATA')
                
                row = box.row()
                col = row.column(align=True)
                
                col.prop(
                    data=driver.variables[i].targets[0],
                    property='transform_type',
                    text=core.strings['Type'],
                    translate=False)
                
                if driver.variables[i].targets[0].transform_type in ('ROT_X', 'ROT_Y', 'ROT_Z', 'ROT_W'):
                    col.prop(
                        data=driver.variables[i].targets[0],
                        property='rotation_mode',
                        text=core.strings['Mode'],
                        translate=False)
                
                col.prop(
                    data=driver.variables[i].targets[0],
                    property='transform_space',
                    text=core.strings['Space'])
            elif driver.variables[i].type == 'ROTATION_DIFF':
                for j, target in enumerate(driver.variables[i].targets):
                    col = box.column(align=True)
                    
                    col.prop(
                        data=target,
                        property='id',
                        text=core.strings['Object %s'] % str(j + 1),
                        expand=True)
                    
                    if target.id and target.id.type == 'ARMATURE':
                        col.prop_search(
                            data=target,
                            property='bone_target',
                            search_data=target.id.data,
                            search_property='bones',
                            text=core.strings['Bone'],
                            icon='BONE_DATA')
            elif driver.variables[i].type == 'LOC_DIFF':
                for j, target in enumerate(driver.variables[i].targets):
                    row = box.column()
                    col = row.column(align=True)
                    
                    col.prop(
                        data=target,
                        property='id',
                        text=core.strings['Object %s'] % str(j + 1),
                        expand=True)
                    
                    if target.id and target.id.type == 'ARMATURE':
                        col.prop_search(
                            data=target,
                            property='bone_target',
                            search_data=target.id.data,
                            search_property='bones',
                            text=core.strings['Bone'],
                            icon='BONE_DATA')
                    
                    col.prop(
                        data=target,
                        property='transform_space',
                        text=core.strings['Space'])
