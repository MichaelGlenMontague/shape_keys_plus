# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name" : "Shape Keys+",
    "author" : "Michael Glen Montague",
    "version" : (1, 3, 4),
    "blender" : (2, 82, 7),
    "location" : "Properties > Data",
    "description" : "Adds a panel with extra options for creating, sorting, viewing, and driving shape keys.",
    "warning" : "",
    "wiki_url" : "",
    "category" : "Object"
}

import bpy
import bl_ui
import re


########################################################################
############################### CLASSES ################################
########################################################################


class AddonProperties(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    def update_hide_default(self, context):
        if self.hide_default:
            bpy.utils.unregister_class(bl_ui.properties_data_mesh.DATA_PT_shape_keys)
        else:
            bpy.utils.register_class(bl_ui.properties_data_mesh.DATA_PT_shape_keys)
    
    enable_debugging : \
        bpy.props.BoolProperty(
            name="Enable Debugging",
            description="Enables unstable operations for debugging",
            default=False)
    
    hide_default : \
        bpy.props.BoolProperty(
            name="Hide Default Panel",
            description="Hides the default Shape Keys panel",
            default=True,
            update=update_hide_default)
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        
        row.prop(
            data=self,
            property='enable_debugging')
        
        row.prop(
            data=self,
            property='hide_default')


class Selection(bpy.types.PropertyGroup):
    value : bpy.props.BoolProperty()


class KeyProperties(bpy.types.PropertyGroup):
    selections : bpy.props.CollectionProperty(type=Selection)


class SceneProperties(bpy.types.PropertyGroup):
    shape_key_add_placement : \
        bpy.props.EnumProperty(
            name="Add Shape Placement",
            items=(
                ('TOP', "Top",
                 ("Place new shape keys at the top of the list."),
                 'TRIA_UP_BAR', 0),
                ('ABOVE', "Above",
                 ("Place new shape keys below the active key."),
                 'TRIA_UP', 1),
                ('BELOW', "Below",
                 ("Place new shape keys under the active key."),
                 'TRIA_DOWN', 2),
                ('BOTTOM', "Bottom",
                 ("Place new shape keys at the bottom of the list."),
                 'TRIA_DOWN_BAR', 3)
            ),
            default='BELOW')
    
    shape_key_parent_placement : \
        bpy.props.EnumProperty(
            name="Parenting Placement",
            items=(
                ('TOP', "Top",
                 ("Place newly parented shape keys "
                  "at the top of the list."),
                 'TRIA_UP_BAR', 0),
                ('BOTTOM', "Bottom",
                 ("Place newly parented shape keys "
                  "at the bottom of the list."),
                 'TRIA_DOWN_BAR', 1)
            ),
            default='BOTTOM')
    
    shape_key_unparent_placement : \
        bpy.props.EnumProperty(
            name="Unparenting Placement",
            items=(
                ('TOP', "Top",
                 ("Place unparented shape keys at "
                  "the top of the new directory."),
                 'TRIA_UP_BAR', 0),
                ('ABOVE', "Above",
                 ("Place unparented shape keys above the folder."),
                 'TRIA_UP', 1),
                ('BELOW', "Below",
                 ("Place unparented shape keys below the folder."),
                 'TRIA_DOWN', 2),
                ('BOTTOM', "Bottom",
                 ("Place unparented shape keys at the bottom of the new directory."),
                 'TRIA_DOWN_BAR', 3)
            ),
            default='ABOVE')
    
    shape_key_auto_parent : \
        bpy.props.BoolProperty(
            name="Auto Parent",
            description="Automatically parent new shapes to the active folder",
            default=True)
    
    shape_key_indent_scale : \
        bpy.props.IntProperty(
            name="Indentation",
            description="Indentation of folder contents",
            min=0,
            max=8,
            default=4)
    
    folder_icon_pair : \
        bpy.props.IntProperty(
            default=0)
    
    folder_icon_swap : \
        bpy.props.BoolProperty(
            default=False)
    
    driver_visible : \
        bpy.props.BoolProperty(
            name="Show Driver",
            default=True)
    
    show_filtered_folder_contents : \
        bpy.props.BoolProperty(
            name="Show Filtered Folder Contents",
            description="Show contents of a folder that is being filtered, even if its contents don't match the filter",
            default=True)
    
    shape_key_limit_to_active : \
        bpy.props.BoolProperty(
            name="Show Active Shapes Only",
            description="Only show shape keys with a value above a certain threshold",
            default=False)
    
    filter_active_threshold : \
        bpy.props.FloatProperty(
            name="Active Threshold",
            description="Only show shape keys above this value",
            soft_min = 0.0,
            soft_max = 1.0,
            default = 0.001,
            step=1,
            precision=3)
    
    filter_active_below : \
        bpy.props.BoolProperty(
            name="Flip Active Threshold",
            description="Only show values lower than the threshold instead of higher",
            default=False)


########################################################################
############################### UTILITY ################################
########################################################################


class utils:
    prefix = "SKP"
    folder = ".F"
    children = ".C"
    expand = ".E"
    icons = ".I"
    icons_swap = ".IS"
    
    # Value that will be given to all children as the parent count.
    folder_default = 1
    # Number of shape keys under the folder.
    children_default = 0
    # 0 = collapse, 1 = expand
    expand_default = 1
    # Block for whether or not a folder has its icon pair reversed.
    # 0 = normal, 1 = swap
    icons_swap_default = 0
    
    icon_pairs_standard = (
        ('DISCLOSURE_TRI_DOWN', 'DISCLOSURE_TRI_RIGHT', "Outliner", "", 0),
        ('TRIA_DOWN', 'TRIA_RIGHT', "Bold", "", 1),
        ('DOWNARROW_HLT', 'RIGHTARROW', "Wire", "", 2),
        ('SORT_ASC', 'FORWARD', "Arrow", "", 3),
        ('LAYER_ACTIVE', 'LAYER_USED', "Small", "", 4),
        ('RADIOBUT_ON', 'RADIOBUT_OFF', "Big", "", 5),
        ('DOT', 'REC', "Pulsar", "", 6),
    )
    
    icon_pairs_special = (
        ('KEY_DEHLT', 'KEY_HLT', "Polarity", "", 7),
        ('KEYFRAME_HLT', 'KEYFRAME', "Keyframe", "", 8),
        ('MARKER_HLT', 'MARKER', "Marker", "", 9),
        ('PMARKER_ACT', 'PMARKER_SEL', "Diamond", "", 10),
        ('SOLO_ON', 'SOLO_OFF', "Star", "", 11),
        ('CHECKBOX_HLT', 'CHECKBOX_DEHLT', "Checkbox", "", 12),
    )
    
    icon_pairs_misc = (
        ('PINNED', 'UNPINNED', "Pin", "", 12),
        ('PROP_ON', 'PROP_OFF', "Proportional", "", 13),
        ('ZOOM_OUT', 'ZOOM_IN', "Magnifier", "", 14),
        ('MESH_PLANE', 'SHADING_BBOX', "Continuity", "", 15),
        ('DECORATE_UNLOCKED', 'DECORATE_LOCKED', "Lock", "", 16),
        ('RESTRICT_COLOR_ON', 'RESTRICT_COLOR_OFF', "Tabs", "", 17),
        ('HIDE_OFF', 'HIDE_ON', "Eye", "", 18),
        ('RESTRICT_SELECT_OFF', 'RESTRICT_SELECT_ON', "Cursor", "", 19),
        ('RESTRICT_VIEW_OFF', 'RESTRICT_VIEW_ON', "Monitor", "", 20),
        ('RESTRICT_RENDER_OFF', 'RESTRICT_RENDER_ON', "Camera", "", 21),
        ('MODIFIER_ON', 'MODIFIER_OFF', "Modifier", "", 22),
        ('MUTE_IPO_ON', 'MUTE_IPO_OFF', "Mute", "", 23),
        ('SMOOTHCURVE', 'SPHERECURVE', "Squeeze", "", 24),
        ('SHARPCURVE', 'ROOTCURVE', "Pinch", "", 25),
        ('SNAP_ON', 'SNAP_OFF', "Magnet", "", 26),
        ('FREEZE', 'MATFLUID', "Precipitation", "", 27),
        ('ALIGN_TOP', 'ALIGN_BOTTOM', "Switch", "", 28),
        ('TEXT', 'ASSET_MANAGER', "Good Read", "", 29)
    )
    
    icon_pairs = \
        icon_pairs_standard[:] + \
        icon_pairs_special[:] + \
        icon_pairs_misc[:]
    
    cache = {
        'pointers' : [],
        'parents' : [],
        'children' : []
    }
    
    @classmethod
    def update_cache(cls, override=False):
        obj = bpy.context.object
        
        if obj:
            shape_keys = obj.data.shape_keys
            
            if shape_keys:
                key_blocks = shape_keys.key_blocks
                keys = [kb.as_pointer() for kb in key_blocks]
                
                if cls.cache['pointers'] != keys or override:
                    cls.cache['pointers'] = keys
                    cls.cache['parents'].clear()
                    cls.cache['children'].clear()
                    
                    for kb in key_blocks:
                        parents = cls.get_key_parents(kb)
                        children = cls.get_folder_children(kb)
                        
                        cls.cache['parents'].append(parents)
                        cls.cache['children'].append(children)
        
        return cls.cache
    
    @classmethod
    def create_folder_data(cls,
                           folder=folder_default,
                           children=children_default,
                           expand=expand_default,
                           icons=None,
                           icons_swap=icons_swap_default):
        
        skp = bpy.context.scene.shape_keys_plus
        
        if folder is None:
            folder = folder_default
        if children is None:
            children = children_default
        if expand is None:
            expand = expand_default
        if icons is None:
            icons = skp.folder_icon_pair
        if icons_swap is None:
            icons_swap = icons_swap_default
        
        prefix = cls.prefix
        folder = cls.folder + str(folder)
        children = cls.children + str(children)
        expand = cls.expand + str(expand)
        icons = cls.icons + str(icons)
        icons_swap = cls.icons_swap + str(icons_swap)
        
        return prefix + folder + children + expand + icons + icons_swap
    
    @classmethod
    def get_block(cls, data, block=None):
        if data.startswith(cls.prefix):
            if block is None:
                return data.split(".")
            else:
                data = data.split(".")
                block = re.sub(r"[^A-Za-z]", "", block)
                
                for x in data:
                    if block in x:
                        return x
        
        return None
    
    @classmethod
    def has_block(cls, data, block):
        return cls.get_block(data, block) is not None
    
    @classmethod
    def block_index(cls, data, block):
        data = data.split(".")
        block = re.sub(r"[^A-Za-z]", "", block)
        
        for i, x in enumerate(data):
            if block in x:
                return i
    
    @classmethod
    def block_set(cls, data, block, value):
        if cls.has_block(data, block):
            original = cls.get_block(data, block)
            key = re.sub(r"[^A-Za-z]", "", original)
            
            split = data.split(".")
            index = cls.block_index(data, block)
            
            split[index] = key + str(value)
            
            return ".".join(split)
        
        return data
    
    @classmethod
    def block_value(cls, data, block):
        skp = bpy.context.scene.shape_keys_plus
        
        if cls.has_block(data, block):
            default = None
            
            if block == cls.folder:
                default = cls.folder_default
            elif block == cls.children:
                default = cls.children_default
            elif block == cls.expand:
                default = cls.expand_default
            elif block == cls.icons:
                default = skp.folder_icon_pair
            elif block == cls.icons_swap:
                default = cls.icons_swap_default
            
            if default is not None:
                value = re.sub(r"\D", "", cls.get_block(data, block))
                
                if value != "":
                    return int(value)
                else:
                    return default
        
        return -1
    
    @classmethod
    def is_key_folder(cls, key):
        return cls.has_block(key.vertex_group, cls.folder)
    
    @classmethod
    def is_key_child_of(cls, key, folder):
        return key.name in [c.name for c in cls.get_folder_children(folder)]
    
    @classmethod
    def get_icon_pair(cls, id, d=0):
        return next((p for p in cls.icon_pairs if p[-1] == id), cls.icon_pairs[d])
    
    @classmethod
    def get_folder_capacity(cls, folder):
        capacity = 0
        
        context = bpy.context
        
        if cls.is_key_folder(folder):
            shape_keys = context.object.data.shape_keys
            folder_index = cls.get_key_index(folder)
            
            s = folder_index + 1
            e = s + cls.get_folder_children_value(folder)
            
            i = s
            
            while i < e:
                if len(shape_keys.key_blocks) > i:
                    key = shape_keys.key_blocks[i]
                    
                    capacity += 1
                    
                    if cls.is_key_folder(key):
                        e += cls.get_folder_children_value(key)
                    
                    i += 1
        
        return capacity
    
    @classmethod
    def get_folder_children(cls, folder):
        children = []
        
        context = bpy.context
        
        if cls.is_key_folder(folder):
            shape_keys = context.object.data.shape_keys
            folder_index = shape_keys.key_blocks.find(folder.name)
            index = folder_index + 1
            capacity = cls.get_folder_capacity(folder)
            
            for i in range(index, index + capacity):
                if len(shape_keys.key_blocks) > i:
                    children.append(shape_keys.key_blocks[i])
        
        return children
    
    @classmethod
    def get_key_parent(cls, key):
        context = bpy.context
        
        if key:
            shape_keys = context.object.data.shape_keys
            index = cls.get_key_index(key)
            i = index - 1
            
            while i >= 0:
                key = shape_keys.key_blocks[i]
                is_folder = cls.is_key_folder(key)
                capacity = cls.get_folder_capacity(key)
                
                if is_folder and capacity > 0:
                    if i <= index <= i + capacity:
                        return key
                
                i -= 1
        
        return None
    
    @classmethod
    def get_key_parents(cls, key):
        context = bpy.context
        
        parents = []
        
        if key:
            shape_keys = context.object.data.shape_keys
            index = cls.get_key_index(key)
            i = index - 1
            
            while i >= 0:
                key = shape_keys.key_blocks[i]
                is_folder = cls.is_key_folder(key)
                capacity = cls.get_folder_capacity(key)
                
                if is_folder and capacity > 0:
                    if i <= index <= i + capacity:
                        parents.append(key)
                        
                        if cls.get_folder_stack_value(key) < 2:
                            break
                
                i -= 1
        
        return parents
    
    @classmethod
    def get_key_index(cls, key):
        context = bpy.context
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if shape_keys and shape_keys.key_blocks:
            return shape_keys.key_blocks.find(key.name)
        
        return -1
    
    @classmethod
    def get_key_siblings(cls, key):
        siblings = [None, None]
        
        context = bpy.context
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        parents = cls.get_key_parents(key)
        parent = get(parents, 0)
        index = cls.get_key_index(key)
        capacity = cls.get_folder_capacity(key)
        
        previous_index = index - 1
        next_index = index + capacity + 1
        
        ###########################
        ######## NEIGHBORS ########
        ###########################
        
        # Get references to the keys in the immediate proximity.
        if previous_index >= 0:
            previous_key = key_blocks[previous_index]
        else:
            previous_key = None
        
        if next_index < len(key_blocks):
            next_key = key_blocks[next_index]
        else:
            next_key = None
        
        ###############################
        ######## OLDER SIBLING ########
        ###############################
        
        # Find out whether or not those keys are siblings to this key.
        if previous_key:
            previous_key_parents = cls.get_key_parents(previous_key)
            
            if len(previous_key_parents) > 0:
                previous_key_parent = previous_key_parents[0]
            else:
                previous_key_parent = None
            
            if parent:
                if previous_key_parent:
                    if previous_key_parent.name == parent.name:
                        # Two keys with the same parent are siblings.
                        siblings[0] = previous_key
                    elif previous_key.name != parent.name:
                        # If the previous key's parent is not the
                        # current key's parent, the sibling key
                        # is the parent of the previous key.
                        offset = len(previous_key_parents) - len(parents) - 1
                        
                        siblings[0] = previous_key_parents[offset]
            else:
                if previous_key_parent:
                    # If the current key has no parent but the previous
                    # key does, this key's sibling is that key's parent.
                    siblings[0] = previous_key_parents[-1]
                else:
                    # If neither of these neighboring keys
                    # have any parents, they are siblings.
                    siblings[0] = previous_key
        
        #################################
        ######## YOUNGER SIBLING ########
        #################################
        
        if next_key:
            next_key_parents = cls.get_key_parents(next_key)
            
            if len(next_key_parents) > 0:
                next_key_parent = next_key_parents[0]
            else:
                next_key_parent = None
            
            if parent:
                if next_key_parent:
                    if next_key_parent.name == parent.name:
                        # Two keys with the same parent are siblings.
                        siblings[1] = next_key
            else:
                if next_key_parent:
                    # It's not possible for the next key to have
                    # a parent if the current key doesn't have any.
                    pass
                else:
                    siblings[1] = next_key
        
        return siblings
    
    @classmethod
    def shift_folder_children_value(cls, key, amount):
        if cls.has_block(key.vertex_group, cls.children):
            destination = cls.block_value(key.vertex_group, cls.children) + amount
            key.vertex_group = cls.block_set(key.vertex_group, cls.children, max(0, destination))
    
    @classmethod
    def shift_folder_stack_value(cls, key, amount):
        if cls.has_block(key.vertex_group, cls.folder):
            destination = cls.block_value(key.vertex_group, cls.folder) + amount
            key.vertex_group = cls.block_set(key.vertex_group, cls.folder, max(1, destination))
    
    @classmethod
    def set_folder_children_value(cls, key, val):
        if cls.has_block(key.vertex_group, cls.folder):
            key.vertex_group = cls.block_set(key.vertex_group, cls.children, val)
    
    @classmethod
    def set_folder_stack_value(cls, key, val):
        if cls.has_block(key.vertex_group, cls.folder):
            key.vertex_group = cls.block_set(key.vertex_group, cls.folder, val)
    
    @classmethod
    def get_folder_children_value(cls, key):
        return cls.block_value(key.vertex_group, cls.children)
    
    @classmethod
    def get_folder_stack_value(cls, key):
        return cls.block_value(key.vertex_group, cls.folder)
    
    @classmethod
    def toggle_folder(cls, key, expand=None):
        if cls.is_key_folder(key):
            original = cls.block_value(key.vertex_group, cls.expand)
            
            if expand is None:
                toggle = 1 if original == 0 else 0
            else:
                toggle = 1 if expand else 0
            
            key.vertex_group = cls.block_set(key.vertex_group, cls.expand, toggle)
    
    @classmethod
    def get_key_driver(cls, shape_keys, key):
        anim = shape_keys.animation_data
        data_path = "key_blocks[\"" + key.name + "\"].value"
        
        if anim and anim.drivers:
            for fcu in anim.drivers:
                if fcu.data_path == data_path:
                    return fcu.driver
        
        return None
    
    @classmethod
    def update_driver(cls, driver):
        if driver:
            driver.expression += " "
            driver.expression = driver.expression[:-1]
    
    @classmethod
    def reconstruct_driver_variables(cls, driver, source):
        data = []
        
        for var in source:
            data.append({
                'name' : var.name,
                'type' : var.type,
                'targets' : [{
                    'id' : target.id,
                    'id_type' : target.id_type,
                    'data_path' : target.data_path,
                    'bone_target' : target.bone_target,
                    'transform_type' : target.transform_type,
                    'transform_space' : target.transform_space
                } for j, target in enumerate(var.targets)]
            })
        
        while driver.variables:
            driver.variables.remove(driver.variables[0])
        
        for i in range(len(source)):
            new_var = driver.variables.new()
            new_var.name = data[i]['name']
            
            # The type controls the targets, so this comes first.
            new_var.type = data[i]['type']
            
            for j, old_target in enumerate(data[i]['targets']):
                new_target = new_var.targets[j]
                new_target.id = old_target['id']
                
                # Only the "Single Property" type can have its id_type changed.
                if new_var.type == 'SINGLE_PROP':
                    new_target.id_type = old_target['id_type']
                
                new_target.data_path = old_target['data_path']
                new_target.bone_target = old_target['bone_target']
                new_target.transform_type = old_target['transform_type']
                new_target.transform_space = old_target['transform_space']
        
        cls.update_driver(driver)
    
    @classmethod
    def shape_key_selected(cls, index):
        context = bpy.context
        obj = context.object
        shape_keys = obj.data.shape_keys
        
        if not shape_keys:
            return False
        
        return str(index) in shape_keys.shape_keys_plus.selections
    
    @classmethod
    def selected_shape_key_indices(cls):
        context = bpy.context
        obj = context.object
        shape_keys = obj.data.shape_keys
        
        indices = []
        
        if not shape_keys:
            return indices
        
        selections = shape_keys.shape_keys_plus.selections
        
        for i, x in enumerate(selections):
            if x.name.isdigit():
                indices.append(int(x.name))
        
        return sorted(indices)
    
    @classmethod
    def selected_shape_keys(cls):
        context = bpy.context
        obj = context.object
        shape_keys = obj.data.shape_keys
        
        keys = []
        
        if not shape_keys:
            return keys
        
        indices = cls.selected_shape_key_indices()
        
        for index in indices:
            keys.append(shape_keys.key_blocks[index])
        
        return keys
    
    @classmethod
    def shape_key_move_to(cls, origin, destination):
        context = bpy.context
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        obj.active_shape_key_index = origin
        
        active_key = obj.active_shape_key
        active_capacity = cls.get_folder_capacity(active_key)
        
        direction = 'UP' if destination < origin else 'DOWN'
        
        offset = origin + active_capacity + 1
        
        if direction == 'UP':
            move_range = range(origin, destination, -1)
        else:
            move_range = range(origin, destination)
        
        inc = 0
        
        for i in move_range:
            if direction == 'UP':
                block_range = range(origin + inc, offset + inc)
            else:
                block_range = reversed(range(origin + inc, offset + inc))
            
            for j in block_range:
                obj.active_shape_key_index = j
                bpy.ops.object.shape_key_move(type=direction)
            
            inc += -1 if direction == 'UP' else 1
        
        is_folder = active_capacity > 0
        
        if is_folder:
            # Re-selects the folder after moving its children.
            obj.active_shape_key_index = origin + inc
    
    @classmethod
    def apply_add_placement(cls, key, ref):
        context = bpy.context
        skp = context.scene.shape_keys_plus
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        basis_capacity = cls.get_folder_capacity(key_blocks[0])
        
        key_index = cls.get_key_index(key)
        ref_index = cls.get_key_index(ref)
        
        is_ref_folder = cls.is_key_folder(ref)
        
        ref_capacity = cls.get_folder_capacity(ref)
        ref_parents = cls.get_key_parents(ref)
        ref_parent = get(ref_parents, 0)
        
        auto_parent = skp.shape_key_auto_parent and ref_parent
        mode = skp.shape_key_add_placement
        
        if ref_parent:
            ref_parent_index = cls.get_key_index(ref_parent)
            ref_parent_capacity = cls.get_folder_capacity(ref_parent)
        
        # The reference key's highest and lowest-level parents if they exist, otherwise the reference key itself.
        ref_inner = get(ref_parents, 0, ref)
        ref_inner_index = cls.get_key_index(ref_inner)
        ref_inner_capacity = cls.get_folder_capacity(ref_inner)
        
        ref_outer = get(ref_parents, -1, ref)
        ref_outer_index = cls.get_key_index(ref_outer)
        ref_outer_capacity = cls.get_folder_capacity(ref_outer)
        
        if mode == 'TOP':
            if auto_parent:
                placement = ref_inner_index + 1
            else:
                if ref_outer_index == 0:
                    placement = 0
                else:
                    placement = basis_capacity + 1
        elif mode == 'ABOVE':
            if auto_parent:
                placement = ref_index
            else:
                placement = ref_outer_index
        elif mode == 'BELOW':
            if auto_parent:
                placement = ref_index + ref_capacity + 1
            else:
                placement = ref_outer_index + ref_outer_capacity + 1
        elif mode == 'BOTTOM':
            if auto_parent:
                placement = ref_inner_index + ref_inner_capacity
            else:
                placement = key_index
        
        cls.shape_key_move_to(key_index, placement)
    
    @classmethod
    def apply_copy_placement(cls, copy, original):
        context = bpy.context
        
        skp = context.scene.shape_keys_plus
        
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        basis_capacity = cls.get_folder_capacity(key_blocks[0])
        
        copy_index = key_blocks.find(copy.name)
        original_index = key_blocks.find(original.name)
        
        is_original_folder = cls.is_key_folder(original)
        
        original_capacity = cls.get_folder_capacity(original)
        original_parents = cls.get_key_parents(original)
        original_parent = get(original_parents, 0)
        
        auto_parent = skp.shape_key_auto_parent and original_parent
        mode = skp.shape_key_add_placement
        
        if original_parent:
            original_parent_index = cls.get_key_index(original_parent)
            original_parent_capacity = cls.get_folder_capacity(original_parent)
        
        original_inner = get(original_parents, 0, original)
        original_inner_index = cls.get_key_index(original_inner)
        original_inner_capacity = cls.get_folder_capacity(original_inner)
        
        # The original key's lowest-level parent if it exists, otherwise the original key itself.
        original_outer = get(original_parents, -1, original)
        original_outer_index = cls.get_key_index(original_outer)
        original_outer_capacity = cls.get_folder_capacity(original_outer)
        
        if mode == 'TOP':
            if auto_parent:
                placement = original_inner_index + 1
            else:
                if original_outer_index == 0:
                    placement = 0
                else:
                    placement = basis_capacity + 1
        elif mode == 'ABOVE':
            if auto_parent:
                placement = original_index
            else:
                placement = original_outer_index
        elif mode == 'BELOW':
            if auto_parent:
                placement = original_index + original_capacity + 1
            else:
                placement = original_outer_index + original_outer_capacity + 1
        elif mode == 'BOTTOM':
            if auto_parent:
                # Add 1 because the copy is an additional child.
                placement = original_inner_index + original_inner_capacity + 1
            else:
                placement = copy_index
        
        cls.shape_key_move_to(copy_index, placement)
    
    @classmethod
    def apply_parent_placement(cls, key, parent):
        context = bpy.context
        skp = context.scene.shape_keys_plus
        obj = context.object
        
        key_index = cls.get_key_index(key)
        parent_index = cls.get_key_index(parent)
        
        key_capacity = cls.get_folder_capacity(key)
        
        # A replica of the parent's capacity after it is shifted.
        parent_capacity = cls.get_folder_capacity(parent) + cls.get_folder_capacity(key) + 1
        
        mode = skp.shape_key_parent_placement
        
        if mode == 'TOP':
            placement = parent_index + 1
        elif mode == 'BOTTOM':
            placement = parent_index + parent_capacity - key_capacity
        
        # Account for the shifting of indices after the key is moved.
        placement += (-1 - key_capacity) if placement > key_index else 0
        
        cls.shape_key_move_to(key_index, placement)
    
    @classmethod
    def apply_unparent_placement(cls, key, clear):
        context = bpy.context
        skp = context.scene.shape_keys_plus
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        key_index = cls.get_key_index(key)
        key_capacity = cls.get_folder_capacity(key)
        
        basis_capacity = cls.get_folder_capacity(key_blocks[0])
        
        parents = cls.get_key_parents(key)
        parent = parents[0]
        outer_parent = parents[-1]
        grandparent = get(parents, 1)
        
        parent_index = cls.get_key_index(parent)
        parent_capacity = cls.get_folder_capacity(parent)
        
        outer_parent_index = cls.get_key_index(outer_parent)
        outer_parent_capacity = cls.get_folder_capacity(outer_parent)
        
        if grandparent:
            grandparent_index = cls.get_key_index(grandparent)
            grandparent_capacity = cls.get_folder_capacity(grandparent)
        
        mode = skp.shape_key_unparent_placement
        
        if mode == 'TOP':
            if clear:
                if outer_parent_index == 0:
                    placement = 0
                else:
                    placement = basis_capacity + 1
            else:
                if grandparent:
                    placement = grandparent_index + 1
                else:
                    if parent_index == 0:
                        placement = 0
                    else:
                        placement = 1
        elif mode == 'ABOVE':
            if clear:
                placement = outer_parent_index
            else:
                placement = parent_index
        elif mode == 'BELOW':
            if clear:
                placement = outer_parent_index + outer_parent_capacity + 1
            else:
                placement = parent_index + parent_capacity + 1
        elif mode == 'BOTTOM':
            if clear:
                placement = len(key_blocks)
            else:
                if grandparent:
                    placement = grandparent_index + grandparent_capacity + 1
                else:
                    # + 1 doesn't need to be added because the length of key_blocks is already 1 extra.
                    placement = len(key_blocks)
        
        # Account for the shifting of indices after the key is moved.
        placement += (-1 - key_capacity) if placement > key_index else 0
        
        cls.shape_key_move_to(key_index, placement)


class Metadata:
    key = None
    index = 0
    
    parents = []
    children = []
    family = []
    is_folder = False
    stack = 0
    is_parented = False
    first_parent = None
    last_parent = None
    capacity = 0
    has_children = False
    first_child = None
    last_child = None
    first_child_index = 0
    last_child_index = 0
    is_first_child = False
    is_last_child = False
    previous_key = None
    next_key = None
    
    def __init__(self, key, index):
        context = bpy.context
        obj = context.object
        
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        self.key = key
        self.index = index
        
        self.parents = utils.get_key_parents(self.key)
        self.children = utils.get_folder_children(self.key)
        self.is_folder = utils.is_key_folder(self.key)
        self.stack = len(self.parents)
        self.is_parented = self.stack > 0
        
        if self.is_parented:
            self.first_parent = self.parents[0]
            self.last_parent = self.parents[-1]
            
            self.siblings = utils.get_folder_children(self.first_parent)
        else:
            self.siblings = key_blocks
        
        self.capacity = len(self.children)
        self.has_children = self.capacity > 0
        
        if self.has_children:
            self.first_child = self.children[0]
            self.last_child = self.children[-1]
            
            self.first_child_index = key_blocks.find(self.first_child.name)
            self.last_child_index = key_blocks.find(self.last_child.name)
        
        self.is_first_child = self.key.name == self.siblings[0].name
        self.is_last_child = self.key.name == self.siblings[-1].name
        
        if index > 0:
            self.previous_key = key_blocks[index - 1]
        else:
            self.previous_key = None
        
        next_index = index + self.capacity + 1
        
        if len(key_blocks) > next_index:
            self.next_key = key_blocks[next_index]
        else:
            self.next_key = None
    
    def __eq__(self, other):
        if hasattr(self, 'key') and hasattr(other, 'key'):
            return self.key.name == other.key.name
        
        return False
    
    def __ne__(self, other):
        return not self == other
    
    def print_data(self):
        print("Key:", self.key.name)
        print("Index:", self.index)
        print("Parent:", self.parents[0].name if self.is_parented else "None")
        print("Is Folder:", self.is_folder)
        print("Children:", self.capacity if self.has_children else "None")
        
        for c in self.children:
            t = " "
            
            for x in utils.get_key_parents(c):
                t += " "
            
            print(t + c.name)
        
        print("\n")


class Debug:
    @classmethod
    def print_skp_data(cls):
        data = skp_data()
        
        for d in data:
            d.print_data()


def get(l, i, d=None):
    """Returns the value of l[i] if possible, otherwise d."""
    
    if type(l) in (dict, set):
        return l[i] if i in l else d
    
    try:
        return l[i]
    except (IndexError, KeyError, TypeError):
        return d


def evaluate():
    data = []
    
    context = bpy.context
    obj = context.object
    key_blocks = obj.data.shape_keys.key_blocks
    
    for index, key in enumerate(key_blocks):
        data.append(Metadata(key=key, index=index))
    
    return data


def metadata(data, key):
    m = None
    
    for d in data:
        if d.key.name == key.name:
            m = d
            break
    
    return m

def hide_modifiers(obj):
    values = []
    
    for modifier in obj.modifiers:
        values.append(modifier.show_viewport)
        modifier.show_viewport = False
    
    return obj, values

def show_modifiers(data):
    obj, values = data
    
    for i, modifier in enumerate(obj.modifiers):
        modifier.show_viewport = values[i]

def shape_key_parent(key, parent, sibling=None):
    if key.name == parent.name:
        return
    
    key_parent = utils.get_key_parent(key)
    
    if key_parent:
        utils.shift_folder_children_value(key_parent, -1)
    
    context = bpy.context
    obj = context.object
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    
    # The folder should be open if something is being added to it.
    utils.toggle_folder(parent, True)
    
    if sibling:
        # The sibling is the currently active key during auto parent, if it's not a folder.
        utils.shift_folder_children_value(parent, 1)
        utils.apply_add_placement(key, sibling)
    else:
        utils.apply_parent_placement(key, parent)
        utils.shift_folder_children_value(parent, 1)
    
    if utils.is_key_folder(key):
        children = utils.get_folder_children(key)
        
        old_stack = utils.get_folder_stack_value(key)
        new_stack = utils.get_folder_stack_value(parent)
        
        # Add 1 because the new key will be a child of the new stack.
        stack_offset = (new_stack - old_stack) + 1
        
        utils.shift_folder_stack_value(key, stack_offset)
        
        for c in children:
            if utils.is_key_folder(c):
                utils.shift_folder_stack_value(c, stack_offset)


def shape_key_unparent(key, clear=False):
    parents = utils.get_key_parents(key)
    children = utils.get_folder_children(key)
    
    if not parents:
        return
    
    first_parent = parents[0]
    second_parent = get(parents, 1)
    last_parent = parents[-1]
    
    key_index = utils.get_key_index(key)
    key_capacity = utils.get_folder_capacity(key)
    
    is_key_folder = utils.is_key_folder(key)
    
    first_parent_index = utils.get_key_index(first_parent)
    last_parent_index = utils.get_key_index(last_parent)
    
    first_parent_capacity = utils.get_folder_capacity(first_parent)
    last_parent_capacity = utils.get_folder_capacity(last_parent)
    
    utils.apply_unparent_placement(key, clear)
    utils.shift_folder_children_value(first_parent, -1)
    
    if clear:
        if is_key_folder:
            old_stack = utils.get_folder_stack_value(key)
            
            utils.set_folder_stack_value(key, 1)
            
            for c in children:
                if not utils.is_key_folder(c):
                    continue
                
                stack_offset = utils.get_folder_stack_value(c) - old_stack
                
                utils.set_folder_stack_value(c, 1 + stack_offset)
    else:
        if second_parent:
            utils.shift_folder_children_value(second_parent, 1)
        
        if is_key_folder:
            utils.shift_folder_stack_value(key, -1)
            
            for c in children:
                if not utils.is_key_folder(c):
                    continue
                
                utils.shift_folder_stack_value(c, -1)


def shape_key_add(type='DEFAULT'):
    context = bpy.context
    skp = context.scene.shape_keys_plus
    obj = context.object
    active_key = obj.active_shape_key
    active_index = obj.active_shape_key_index
    active_parent = utils.get_key_parent(active_key)
    
    # Shape Key Creation
    if type == 'FROM_MIX':
        new_key = obj.shape_key_add(from_mix=True)
    elif type == 'FROM_MIX_SELECTED':
        selected = []
        
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        for i, key in enumerate(key_blocks):
            if not utils.shape_key_selected(i):
                if not key.mute:
                    key.mute = True
                    selected.append(i)
        
        new_key = obj.shape_key_add(from_mix=True)
        
        for i in selected:
            key_blocks[i].mute = False
        
        shape_keys.shape_keys_plus.selections.clear()
    else:
        new_key = obj.shape_key_add(from_mix=False)
    
    # Shape Key Naming
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    new_index = len(key_blocks) - 1
    obj.active_shape_key_index = new_index
    
    if type in ('FOLDER', 'PARENT'):
        folder_count = 1
        
        for key in key_blocks:
            if utils.is_key_folder(key):
                folder_count += 1
        
        new_key.vertex_group = utils.create_folder_data()
        new_key.name = "Folder " + str(folder_count)
    else:
        if len(key_blocks) == 1:
            new_key.name = "Basis"
        else:
            new_key.name = "Key " + str(len(key_blocks) - 1)
    
    # Shape Key Placement
    # If there was no original active key, no special placement will be done.
    if active_key:
        is_active_folder = utils.is_key_folder(active_key)
        
        if is_active_folder:
            # Prioritize the selected key as the new key's
            # parent if the selected key is a folder.
            parent = active_key
        elif active_parent:
            # If the selected key isn't a folder,
            # use its parent as the new key's parent.
            parent = active_parent
        else:
            # Only consider auto-parenting if the current context
            # allows for a key to be used as the new key's parent.
            parent = None
        
        if type == 'PARENT':
            if active_parent:
                # This counts as manually parenting, so it works even when auto parent is turned off.
                shape_key_parent(new_key, active_parent)
            
            # This part ignores all placement options, and it is assumed that the
            # new folder should take the location of whatever is being parented to it.
            utils.shape_key_move_to(utils.get_key_index(new_key), active_index)
        else:
            if skp.shape_key_auto_parent and parent:
                if is_active_folder:
                    shape_key_parent(new_key, parent)
                else:
                    shape_key_parent(new_key, parent, sibling=active_key)
            else:
                utils.apply_add_placement(new_key, active_key)
    
    return new_key


def shape_key_remove(type='DEFAULT', index=-1):
    context = bpy.context
    skp = context.scene.shape_keys_plus
    obj = context.object
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    
    if index == -1:
        active_index = obj.active_shape_key_index
    else:
        active_index = index
    
    active_key = key_blocks[active_index]
    basis_key = shape_keys.reference_key
    
    previous_index = active_index - 1
    previous_key = key_blocks[previous_index] if previous_index >= 0 else None
    
    next_index = active_index + 1
    next_key = key_blocks[next_index] if next_index < len(key_blocks) else None
    
    active_key_parent = utils.get_key_parent(active_key)
    previous_key_parent = utils.get_key_parent(previous_key) if previous_key else None
    next_key_parent = utils.get_key_parent(next_key) if next_key else None
    
    siblings = utils.get_key_siblings(active_key)
    
    is_active_folder = utils.is_key_folder(active_key)
    active_children = utils.get_folder_children(active_key)
    active_capacity = len(active_children)
    
    if type == 'CLEAR':
        bpy.ops.object.shape_key_remove(all=True)
    elif type == 'DEFAULT':
        obj.active_shape_key_index = active_index
        
        bpy.ops.object.shape_key_remove()
        
        if active_key_parent:
            utils.shift_folder_children_value(active_key_parent, -1)
        
        # The list of children will be empty if this key isn't a folder.
        for c in active_children:
            obj.active_shape_key_index = utils.get_key_index(c)
            
            bpy.ops.object.shape_key_remove()
        
        # Fix the active index.
        if siblings[0] and siblings[0].name != basis_key.name:
            obj.active_shape_key_index = utils.get_key_index(siblings[0])
        elif siblings[1]:
            obj.active_shape_key_index = utils.get_key_index(siblings[1])
    elif type == 'DEFAULT_SELECTED':
        selections = utils.selected_shape_keys()
        keys = []
        
        removing_active = False
        
        # Search for keys by name and remove them.
        for key in selections:
            if key != active_key:
                keys.append(key)
        
        # Remove the active key last so that the active index automatically corrects itself.
        if utils.shape_key_selected(active_index):
            removing_active = True
            keys.append(active_key)
        
        for key in keys:
            obj.active_shape_key_index = utils.get_key_index(key)
            
            key_parent = utils.get_key_parent(key)
            
            bpy.ops.object.shape_key_remove()
            
            if key_parent:
                utils.shift_folder_children_value(key_parent, -1)
        
        if not removing_active:
            obj.active_shape_key_index = utils.get_key_index(active_key)
        
        shape_keys.shape_keys_plus.selections.clear()


def shape_key_move(type, index=-1):
    context = bpy.context
    skp = context.scene.shape_keys_plus
    obj = context.object
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    data = evaluate()
    
    modifiers = hide_modifiers(obj)
    
    if index == -1:
        index = obj.active_shape_key_index
    
    direction = 'UP' if type in ('UP', 'TOP') else 'DOWN'
    
    active_metadata = data[index]
    active_key = active_metadata.key
    
    next_key = active_metadata.previous_key if type in ('UP', 'TOP') else active_metadata.next_key
    next_metadata = metadata(data, next_key) if next_key else None
    parent_metadata = metadata(data, active_metadata.first_parent) if active_metadata.first_parent else None
    
    parent_key = parent_metadata.key if parent_metadata else None
    basis_key = key_blocks[0]
    basis_metadata = data[0]
    last_key = key_blocks[-1]
    last_metadata = data[-1]
    
    next_parent_metadata = \
        metadata(data, next_metadata.first_parent) if \
        next_metadata and next_metadata.first_parent else \
        None
    
    def is_active_folder():
        return active_metadata.is_folder
    
    def is_next_folder():
        return next_metadata and next_metadata.is_folder
    
    def is_active_only_child():
        if parent_metadata:
            is_only_child = utils.get_folder_children_value(parent_key) == 1
        else:
            is_only_child = len(key_blocks) == 1
        
        return is_only_child
    
    def is_active_first_child():
        if parent_metadata:
            is_first_child = active_metadata.is_first_child
        else:
            is_first_child = active_key.name == key_blocks[0].name
        
        return is_first_child
    
    def is_active_last_child():
        if active_metadata.has_children:
            if parent_metadata:
                is_last_child = active_metadata.last_child.name == parent_metadata.last_child.name
            else:
                is_last_child = active_metadata.last_child.name == last_key.name
        else:
            is_last_child = active_metadata.is_last_child
        
        return is_last_child
    
    def is_next_last_child():
        return next_metadata and next_metadata.is_last_child
    
    def move(index, direction):
        """Moves the shape key and all in its capacity range."""
        
        capacity = active_metadata.capacity
        is_folder = capacity > 0
        offset = index + capacity + 1
        
        if direction == 'UP':
            r = range(index, offset)
        else:
            r = reversed(range(index, offset))
        
        for i in r:
            obj.active_shape_key_index = i
            bpy.ops.object.shape_key_move(type=direction)
        
        if is_folder:
            # Re-selects the folder after moving its children.
            obj.active_shape_key_index = index - 1 if direction == 'UP' else index + 1
    
    def move_to_top(folder_metadata):
        if folder_metadata:
            offset = folder_metadata.first_child_index
            
            for i in range(index, offset, -1):
                move(i, 'UP')
        else:
            basis_capacity = basis_metadata.capacity + 1
            
            offset = basis_capacity if index > basis_capacity else 0
            
            for i in range(index, offset, -1):
                move(i, 'UP')
    
    def move_to_bottom(folder_metadata):
        if folder_metadata:
            offset = folder_metadata.last_child_index - active_metadata.capacity
            
            for i in range(index, offset):
                move(i, 'DOWN')
        else:
            offset = last_metadata.index - active_metadata.capacity
            
            for i in range(index, offset):
                move(i, 'DOWN')
    
    def skip_over_folder(next_folder_metadata):
        # The "stack" is the number of parents the key has.
        active_stack = active_metadata.stack
        folder_stack = next_folder_metadata.stack
        
        if folder_stack > active_stack:
            # Get the next folder's parent that matches the
            # parent of the active key, in case the next
            # folder is the last child of multiple folders.
            #
            # folder stack          = 4
            # active stack          = 2
            # common parent index   = 4 - (2 + 1) = 1
            # common parent         = parents[1]
            common_parent_index = folder_stack - (active_stack + 1)
            parent = next_folder_metadata.parents[common_parent_index]
            
            # Update the folder to skip over a lower-level parent.
            next_folder_metadata = metadata(data, parent)
        
        if direction == 'UP':
            offset = index - next_folder_metadata.capacity
            r = range(index, offset - 1, -1)
        else:
            offset = index + next_folder_metadata.capacity
            r = range(index, offset + 1)
        
        for i in r:
            move(i, direction)
    
    if is_active_only_child():
        # The key can't be moved if it's the only key in its local space.
        pass
    elif type == 'TOP':
        # Move the active key to the top of the specified folder's space, or the global space if no folder exists.
        move_to_top(parent_metadata)
    elif type == 'BOTTOM':
        # Move the active key to the bottom of the specified folder's space, or the global space if no folder exists.
        move_to_bottom(parent_metadata)
    elif is_active_first_child():
        if type == 'UP':
            # If the active key is the first child in its space,
            # moving up will cause it to loop back around to the bottom.
            move_to_bottom(parent_metadata)
        elif type == 'DOWN':
            if is_next_folder():
                skip_over_folder(next_metadata)
            else:
                move(index, 'DOWN')
    elif is_active_last_child():
        if type == 'UP':
            if is_next_last_child():
                # If moving up while the above key is the last child of another space, skip over that entire space.
                skip_over_folder(next_parent_metadata)
            else:
                move(index, 'UP')
        elif type == 'DOWN':
            # If the active key is the last child in its space,
            # moving down will cause it to loop back around to the top.
            move_to_top(parent_metadata)
    else:
        if type == 'UP':
            if is_next_last_child():
                # If moving up while the above key is the last child in another space, skip over that entire space.
                skip_over_folder(next_parent_metadata)
            else:
                move(index, 'UP')
        elif type == 'DOWN':
            if is_next_folder():
                skip_over_folder(next_metadata)
            else:
                move(index, 'DOWN')
    
    show_modifiers(modifiers)


def shape_key_select(i, v):
    context = bpy.context
    skp = context.scene.shape_keys_plus
    obj = context.object
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    selections = shape_keys.shape_keys_plus.selections
    
    if type(i) == bpy.types.ShapeKey:
        key = i
        i = utils.get_key_index(key)
    elif type(i) == str:
        key = key_blocks[i]
        i = utils.get_key_index(key)
    elif type(i) == int:
        key = key_blocks[i]
    
    valid = i > 0 and not utils.is_key_folder(key)
    
    if not valid:
        return
    
    i = str(i)
    
    if v == True:
        get(selections, i, selections.add()).name = i
    elif v == False:
        while i in selections:
            selections.remove(selections.find(i))


def shape_key_copy(type='DEFAULT'):
    context = bpy.context
    skp = context.scene.shape_keys_plus
    obj = context.object
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    basis_key = shape_keys.reference_key
    
    active_key = obj.active_shape_key
    active_index = obj.active_shape_key_index
    active_name = active_key.name
    active_parent = utils.get_key_parent(active_key)
    active_children = utils.get_folder_children(active_key)
    
    is_active_folder = utils.is_key_folder(active_key)
    
    obj.active_shape_key_index = active_index
    
    def copy(original_key):
        unmuted_keys = []
        
        # Mute all keys other than the original key.
        for kb in key_blocks:
            applicable = kb.mute == False and kb.name != original_key.name and kb.name != basis_key.name
            
            if applicable:
                unmuted_keys.append(kb)
                kb.mute = True
        
        driver = utils.get_key_driver(shape_keys, original_key)
        
        # Store original values.
        old_name = original_key.name
        old_slider_min = original_key.slider_min
        old_slider_max = original_key.slider_max
        old_value = original_key.value
        old_vertex_group = original_key.vertex_group
        old_relative_key = original_key.relative_key
        old_interpolation = original_key.interpolation
        old_mute = original_key.mute
        
        if driver:
            old_driver_type = driver.type
            old_driver_expression = driver.expression
        
        # Prepare shape key for full copy.
        original_key.slider_min = 0.0
        original_key.slider_max = 1.0
        original_key.value = 1.0
        original_key.vertex_group = ""
        original_key.relative_key = basis_key
        original_key.interpolation = bpy.types.ShapeKey.bl_rna.properties['interpolation'].default
        original_key.mute = False
        
        if driver:
            driver.type = 'SCRIPTED'
            driver.expression = "var + " + str(original_key.value)
        
        new_key = obj.shape_key_add(from_mix=True)
        
        # Select the new key, which was sent to the bottom.
        obj.active_shape_key_index = len(key_blocks) - 1
        
        if 'MIRROR' in type:
            use_topology = 'TOPOLOGY' in type
            
            bpy.ops.object.shape_key_mirror(use_topology=use_topology)
            
            if old_name.endswith(".L"):
                old_name = old_name[:-2] + ".R"
            elif old_name.endswith(".R"):
                old_name = old_name[:-2] + ".L"
        
        # Copy original values.
        new_key.name = old_name
        new_key.slider_min = old_slider_min
        new_key.slider_max = old_slider_max
        new_key.value = old_value
        new_key.vertex_group = old_vertex_group
        new_key.relative_key = old_relative_key
        new_key.interpolation = old_interpolation
        new_key.mute = old_mute
        
        # Restore original values.
        original_key.slider_min = old_slider_min
        original_key.slider_max = old_slider_max
        original_key.value = old_value
        original_key.vertex_group = old_vertex_group
        original_key.relative_key = old_relative_key
        original_key.interpolation = old_interpolation
        original_key.mute = old_mute
        
        if driver:
            driver.type = old_driver_type
            driver.expression = old_driver_expression
        
        for key in unmuted_keys:
            key.mute = False
        
        return new_key
    
    if 'SELECTED' in type:
        selections = [key.name for key in utils.selected_shape_keys()]
        copies = []
        
        shape_keys.shape_keys_plus.selections.clear()
        
        for name in selections:
            key = key_blocks[name]
            copy_key = copy(key)
            
            key_parent = utils.get_key_parent(key)
            auto_parent = skp.shape_key_auto_parent and key_parent
            
            utils.apply_copy_placement(copy_key, key)
            
            if auto_parent:
                utils.shift_folder_children_value(key_parent, 1)
            
            copies.append(copy_key)
        
        for key in copies:
            shape_key_select(key, True)
        
        obj.active_shape_key_index = utils.get_key_index(key_blocks[active_name])
    else:
        copy_key = copy(active_key)
        copy_children = []
        
        for c in active_children:
            copy_children.append(copy(c))
        
        auto_parent = skp.shape_key_auto_parent and active_parent
        
        if not auto_parent:
            old_stack = utils.get_folder_stack_value(copy_key)
            
            utils.set_folder_stack_value(copy_key, 1)
            
            for c in copy_children:
                if not utils.is_key_folder(c):
                    continue
                
                stack_offset = utils.get_folder_stack_value(c) - old_stack
                
                utils.set_folder_stack_value(c, 1 + stack_offset)
        
        utils.apply_copy_placement(copy_key, active_key)
        
        if auto_parent:
            utils.shift_folder_children_value(active_parent, 1)
        
        obj.active_shape_key_index = utils.get_key_index(copy_key)
        
        shape_keys.shape_keys_plus.selections.clear()


########################################################################
################################# MENUS ################################
########################################################################


class MESH_MT_skp_shape_key_add_specials(bpy.types.Menu):
    bl_label = "Shape Key Add Specials"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            row = layout.row()
            
            row.menu(
                menu='MESH_MT_skp_shape_key_add_specials_selected',
                text='Selected (' + str(len(selections)) + ')',
                icon='FILE_TICK')
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_add',
            icon='FILE_TEXT',
            text="New Shape From Mix")
        
        op.type = 'FROM_MIX'
        
        row = layout.row()
        
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_add',
            icon='NEWFOLDER',
            text="New Folder")
        
        op.type = 'FOLDER'


class MESH_MT_skp_shape_key_add_specials_selected(bpy.types.Menu):
    bl_label = "Shape Key Add Specials (Selected)"
    
    def draw(self, context):
        layout = self.layout
        
        op = layout.operator(
            operator='object.skp_shape_key_add',
            icon='FILE_TEXT',
            text="New Shape From Mix")
        
        op.type = 'FROM_MIX_SELECTED'


class MESH_MT_skp_shape_key_copy_specials(bpy.types.Menu):
    bl_label = "Shape Key Copy Specials"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            row = layout.row()
            
            row.menu(
                menu='MESH_MT_skp_shape_key_copy_specials_selected',
                text='Selected (' + str(len(selections)) + ')',
                icon='FILE_TICK')
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_copy',
            icon='PASTEFLIPDOWN',
            text="Copy Shape Key, Mirrored")
        
        op.type = 'MIRROR'
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_copy',
            icon='PASTEFLIPDOWN',
            text="Copy Shape Key, Mirrored (Topology)")
        
        op.type = 'MIRROR_TOPOLOGY'


class MESH_MT_skp_shape_key_copy_specials_selected(bpy.types.Menu):
    bl_label = "Shape Key Copy Specials (Selected)"
    
    def draw(self, context):
        layout = self.layout
        
        op = layout.operator(
            operator='object.skp_shape_key_copy',
            icon='PASTEDOWN',
            text="Copy Shape Key")
        
        op.type = 'DEFAULT_SELECTED'
        
        op = layout.operator(
            operator='object.skp_shape_key_copy',
            icon='PASTEFLIPDOWN',
            text="Copy Shape Key, Mirrored")
        
        op.type = 'MIRROR_SELECTED'
        
        op = layout.operator(
            operator='object.skp_shape_key_copy',
            icon='PASTEFLIPDOWN',
            text="Copy Shape Key, Mirrored (Topology)")
        
        op.type = 'MIRROR_TOPOLOGY_SELECTED'


class MESH_MT_skp_shape_key_remove_specials(bpy.types.Menu):
    bl_label = "Shape Key Removal Specials"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            row = layout.row()
            
            row.menu(
                menu='MESH_MT_skp_shape_key_remove_specials_selected',
                text='Selected (' + str(len(selections)) + ')',
                icon='FILE_TICK')
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.skp_shape_key_remove',
            icon='CANCEL',
            text="Clear Shape Keys")
        
        op.type = 'CLEAR'


class MESH_MT_skp_shape_key_remove_specials_selected(bpy.types.Menu):
    bl_label = "Shape Key Removal Specials (Selected)"
    
    def draw(self, context):
        layout = self.layout
        
        op = layout.operator(
            operator='object.skp_shape_key_remove',
            icon='REMOVE',
            text="Remove Shape Key")
        
        op.type = 'DEFAULT_SELECTED'


class MESH_MT_skp_shape_key_other_specials(bpy.types.Menu):
    bl_label = "Other Shape Key Specials"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            row = layout.row()
            
            row.menu(
                menu='MESH_MT_skp_shape_key_other_specials_selected',
                text='Selected (' + str(len(selections)) + ')',
                icon='FILE_TICK')
        
        obj = context.object
        active_key = obj.active_shape_key
        is_active_folder = active_key and utils.is_key_folder(active_key)
        
        if active_key:
            row = layout.row()
            row.enabled = not selections
            
            row.menu(
                menu='OBJECT_MT_skp_shape_key_parent',
                icon='FILE_PARENT')
        
        row = layout.row()
        row.enabled = not selections
        
        if is_active_folder:
            row.menu(
                menu='OBJECT_MT_skp_folder_icon',
                icon='COLOR')
        else:
            row.menu(
                menu='OBJECT_MT_skp_folder_icon',
                icon='COLOR',
                text="Set Default Folder Icon to")
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.shape_key_mirror',
            icon='ARROW_LEFTRIGHT')
        
        op.use_topology = False
        
        row = layout.row()
        row.enabled = not selections
        
        op = row.operator(
            operator='object.shape_key_mirror',
            text="Mirror Shape Key (Topology)",
            icon='ARROW_LEFTRIGHT')
        
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
        
        if __name__ != "__main__":
            preferences = context.preferences.addons[__name__].preferences
            
            if preferences.enable_debugging and active_key:
                layout.operator(
                    operator='object.skp_debug_folder_data',
                    icon='ERROR')
        '''
        else:
            if active_key:
                layout.operator(
                    operator='object.skp_debug_folder_data',
                    icon='ERROR')
        '''


class MESH_MT_skp_shape_key_other_specials_selected(bpy.types.Menu):
    bl_label = "Other Shape Key Specials (Selected)"
    
    def draw(self, context):
        layout = self.layout
        
        layout.menu(
            menu='OBJECT_MT_skp_shape_key_parent_selected',
            text='Set Parent to',
            icon='FILE_PARENT')


class OBJECT_MT_skp_shape_key_parent(bpy.types.Menu):
    bl_label = "Set Parent to"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            layout.enabled = False
        
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if active_key:
            key_blocks = shape_keys.key_blocks
            parents = utils.get_key_parents(active_key)
            parent = get(parents, 0, None)
            
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text='New Folder',
                icon='NEWFOLDER')
            
            op.type = 'NEW'
            op.child = active_key.name
            op.parent = parent.name if parent else ""
            
            if parent:
                # Only show the "Clear Parents" operator if the key has more
                # than one parent, otherwise only the "Unparent" operator.
                if len(parents) > 1:
                    op = layout.operator(
                        operator='object.skp_shape_key_parent',
                        text="Clear Parents",
                        icon='CANCEL')
                    
                    op.type = 'CLEAR'
                    op.child = active_key.name
                    op.parent = parent.name
                
                op = layout.operator(
                    operator='object.skp_shape_key_parent',
                    text="Unparent from " + parent.name,
                    icon='X')
                
                op.type = 'UNPARENT'
                op.child = active_key.name
                op.parent = parent.name
            
            # Only allow parenting to a folder that this shape key isn't already related to.
            children = utils.get_folder_children(active_key)
            
            for key in key_blocks:
                is_folder = utils.is_key_folder(key)
                is_current_key = key == active_key
                is_parent = key == parent
                is_child = key in children
                key_parents = utils.get_key_parents(key)
                valid = is_folder and not is_current_key and not is_parent and not is_child
                
                if valid:
                    op = layout.operator(
                        operator='object.skp_shape_key_parent',
                        text=("  " * len(key_parents)) + key.name,
                        icon='FILE_FOLDER')
                    
                    op.type = 'PARENT'
                    op.child = active_key.name
                    op.parent = key.name


class OBJECT_MT_skp_shape_key_parent_selected(bpy.types.Menu):
    bl_label = "Set Parent to (Selected)"
    
    def draw(self, context):
        layout = self.layout
        
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if active_key:
            key_blocks = shape_keys.key_blocks
            
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text='New Folder',
                icon='NEWFOLDER')
            
            op.type = 'NEW_SELECTED'
            
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text="Clear Parents",
                icon='CANCEL')
            
            op.type = 'CLEAR_SELECTED'
                
            op = layout.operator(
                operator='object.skp_shape_key_parent',
                text="Unparent",
                icon='X')
            
            op.type = 'UNPARENT_SELECTED'
            
            for key in key_blocks:
                is_folder = utils.is_key_folder(key)
                key_parents = utils.get_key_parents(key)
                
                if is_folder:
                    op = layout.operator(
                        operator='object.skp_shape_key_parent',
                        text=("  " * len(key_parents)) + key.name,
                        icon='FILE_FOLDER')
                    
                    op.type = 'PARENT_SELECTED'
                    op.parent = key.name


class OBJECT_MT_skp_folder_icon(bpy.types.Menu):
    bl_label = "Set Folder Icon to"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            layout.enabled = False
        
        skp = context.scene.shape_keys_plus
        obj = context.object
        
        active_key = obj.active_shape_key
        is_active_folder = active_key and utils.is_key_folder(active_key)
        
        icons_default = skp.folder_icon_pair
        icons_default_swap = skp.folder_icon_swap
        
        icon_default_pair = utils.get_icon_pair(icons_default)
        icon_default = icon_default_pair[int(icons_default_swap)]
        icon_default_swap = icon_default_pair[int(not icons_default_swap)]
        
        if is_active_folder:
            icons_block = utils.block_value(active_key.vertex_group, utils.icons)
            icons_swap_block = utils.block_value(active_key.vertex_group, utils.icons_swap) == 1
            
            icon_active_pair = utils.get_icon_pair(icons_block)
            icon_active = icon_active_pair[int(icons_swap_block)]
            icon_active_swap = icon_active_pair[not int(icons_swap_block)]
            
            op = layout.operator(
                operator='object.skp_folder_icon',
                icon=icon_default,
                text=icon_default_pair[2] + " (Default)")
            
            op.icons = icons_default
            op.swap = icons_default_swap
            op.set_as_default = False
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator='object.skp_folder_icon',
                icon=icon_default_swap,
                text="")
            
            layout.separator(factor=0.5)
            
            op = layout.operator(
                operator='object.skp_folder_icon',
                icon=icon_active_swap,
                text="Swap (Active)")
            
            op.icons = icons_block
            op.swap = not icons_swap_block
            op.set_as_default = False
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator='object.skp_folder_icon',
                icon=icon_active,
                text="")
            
            layout.separator(factor=0.5)
        
        layout.menu(
            menu='OBJECT_MT_skp_folder_icons_standard',
            text="Standard")
        
        layout.menu(
            menu='OBJECT_MT_skp_folder_icons_special',
            text="Special")
        
        layout.menu(
            menu='OBJECT_MT_skp_folder_icons_misc',
            text="Miscellaneous")


class OBJECT_MT_skp_folder_icons_standard(bpy.types.Menu):
    bl_label = "Set Folder Icon to"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            layout.enabled = False
        
        skp = context.scene.shape_keys_plus
        obj = context.object
        
        active_key = obj.active_shape_key
        is_active_folder = active_key and utils.is_key_folder(active_key)
        
        for i, p in enumerate(utils.icon_pairs_standard):
            op = layout.operator(
                operator='object.skp_folder_icon',
                icon=p[0],
                text=p[2])
            
            op.icons = p[-1]
            op.swap = False
            op.set_as_default = not is_active_folder
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator='object.skp_folder_icon',
                icon=p[1],
                text=p[3])
            
            if i < len(utils.icon_pairs_standard) - 1:
                layout.separator(factor=0.5)


class OBJECT_MT_skp_folder_icons_special(bpy.types.Menu):
    bl_label = "Set Folder Icon to"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            layout.enabled = False
        
        skp = context.scene.shape_keys_plus
        obj = context.object
        
        active_key = obj.active_shape_key
        is_active_folder = active_key and utils.is_key_folder(active_key)
        
        for i, p in enumerate(utils.icon_pairs_special):
            op = layout.operator(
                operator='object.skp_folder_icon',
                icon=p[0],
                text=p[2])
            
            op.icons = p[-1]
            op.swap = False
            op.set_as_default = not is_active_folder
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator='object.skp_folder_icon',
                icon=p[1],
                text=p[3])
            
            if i < len(utils.icon_pairs_special) - 1:
                layout.separator(factor=0.5)


class OBJECT_MT_skp_folder_icons_misc(bpy.types.Menu):
    bl_label = "Set Folder Icon to"
    
    def draw(self, context):
        selections = utils.selected_shape_keys()
        
        layout = self.layout
        
        if selections:
            layout.enabled = False
        
        skp = context.scene.shape_keys_plus
        obj = context.object
        
        active_key = obj.active_shape_key
        is_active_folder = active_key and utils.is_key_folder(active_key)
        
        for i, p in enumerate(utils.icon_pairs_misc):
            op = layout.operator(
                operator='object.skp_folder_icon',
                icon=p[0],
                text=p[2])
            
            op.icons = p[-1]
            op.swap = False
            op.set_as_default = not is_active_folder
            
            opposite = layout.column()
            opposite.enabled = False
            
            op = opposite.operator(
                operator='object.skp_folder_icon',
                icon=p[1],
                text=p[3])
            
            if i < len(utils.icon_pairs_misc) - 1:
                layout.separator(factor=0.5)


########################################################################
############################## OPERATORS ###############################
########################################################################


class OBJECT_OT_skp_folder_icon(bpy.types.Operator):
    bl_idname = 'object.skp_folder_icon'
    bl_label = "Set As Folder Icon"
    bl_description = "Sets the folder icon"
    bl_options = {'REGISTER', 'UNDO'}
    
    icons : bpy.props.IntProperty(
        options={'HIDDEN'})
    
    swap : bpy.props.BoolProperty(
        name="Swap",
        default=False)
    
    set_as_default : bpy.props.BoolProperty(
        name="Set Default",
        default=False)
    
    def execute(self, context):
        skp = context.scene.shape_keys_plus
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        is_active_folder = active_key and utils.is_key_folder(active_key)
        
        if is_active_folder:
            active_key.vertex_group = utils.block_set(
                active_key.vertex_group,
                utils.icons,
                self.icons)
            
            active_key.vertex_group = utils.block_set(
                active_key.vertex_group,
                utils.icons_swap,
                1 if self.swap else 0)
        
        if self.set_as_default:
            skp.folder_icon_pair = self.icons
            skp.folder_icon_swap = 1 if self.swap else 0
        
        return {'FINISHED'}


class OBJECT_OT_skp_shape_key_parent(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_parent'
    bl_label = "Set As Parent"
    bl_description = "Sets the parent"
    bl_options = {'REGISTER', 'UNDO'}
    
    type : bpy.props.EnumProperty(
        items=(
            ('PARENT', "", ""),
            ('UNPARENT', "", ""),
            ('CLEAR', "", "Unparents the active shape key completely."),
            ('NEW', "", "Creates a new parent for the active shape key."),
            ('PARENT_SELECTED', "", ""),
            ('UNPARENT_SELECTED', "", ""),
            ('CLEAR_SELECTED', "", "Unparents the selected shape keys completely."),
            ('NEW_SELECTED', "", "Creates a new parent for the selected shape keys.")
        ),
        default='PARENT',
        options={'HIDDEN'})
    
    child : bpy.props.StringProperty(options={'HIDDEN'})
    parent : bpy.props.StringProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.object.mode != 'EDIT'
    
    def execute(self, context):
        skp = context.scene.shape_keys_plus
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        selections = [key.name for key in utils.selected_shape_keys()]
        
        shape_keys.shape_keys_plus.selections.clear()
        
        child = key_blocks.get(self.child)
        parent = key_blocks.get(self.parent)
        
        if self.type == 'PARENT':
            shape_key_parent(child, parent)
        elif self.type == 'UNPARENT':
            shape_key_unparent(child)
        elif self.type == 'CLEAR':
            shape_key_unparent(child, clear=True)
        elif self.type == 'NEW':
            shape_key_parent(child, shape_key_add(type='PARENT'))
        elif self.type == 'PARENT_SELECTED':
            children = []
            
            for name in selections:
                child = key_blocks[name]
                child_parent = utils.get_key_parent(child)
                
                if child_parent:
                    utils.shift_folder_children_value(child_parent, -1)
                
                # Set the shape keys in the proper order.
                obj.active_shape_key_index = utils.get_key_index(child)
                bpy.ops.object.shape_key_move(type='BOTTOM')
            
            if skp.shape_key_parent_placement == 'TOP':
                selections = reversed(selections)
            
            for name in selections:
                child = key_blocks[name]
                shape_key_parent(child, parent)
                
                children.append(child)
            
            for child in children:
                shape_key_select(child, True)
        elif self.type == 'UNPARENT_SELECTED':
            children = []
            
            if skp.shape_key_unparent_placement in ('DOWN', 'TOP'):
                selections = reversed(selections)
            
            for name in selections:
                child = key_blocks[name]
                shape_key_unparent(child)
                
                children.append(child)
            
            for child in children:
                shape_key_select(child, True)
        elif self.type == 'CLEAR_SELECTED':
            children = []
            
            if skp.shape_key_unparent_placement in ('DOWN', 'TOP'):
                selections = reversed(selections)
            
            for name in selections:
                child = key_blocks[name]
                shape_key_unparent(child, clear=True)
                
                children.append(child)
            
            for child in children:
                shape_key_select(child, True)
        elif self.type == 'NEW_SELECTED':
            parent = shape_key_add(type='FOLDER')
            children = []
            
            for name in selections:
                child = key_blocks[name]
                shape_key_unparent(child, clear=True)
                
                # Set the shape keys in the proper order.
                obj.active_shape_key_index = utils.get_key_index(child)
                bpy.ops.object.shape_key_move(type='BOTTOM')
            
            if skp.shape_key_parent_placement == 'TOP':
                selections = reversed(selections)
            
            for name in selections:
                child = key_blocks[name]
                shape_key_parent(child, parent)
                
                children.append(child)
            
            for child in children:
                shape_key_select(child, True)
            
            obj.active_shape_key_index = utils.get_key_index(parent)
        
        # Force update SKP cache to ensure that the UI updates.
        utils.update_cache(override=True)
        
        return {'FINISHED'}


class OBJECT_OT_skp_shape_key_add(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_add'
    bl_label = "Add Shape Key"
    bl_description = "Add shape key to the object"
    bl_options = {'REGISTER', 'UNDO'}
    
    type : bpy.props.EnumProperty(
        items=(
            ('DEFAULT', "", ""),
            ('FROM_MIX', "", ""),
            ('FROM_MIX_SELECTED', "", ""),
            ('FOLDER', "", "")
        ),
        default='DEFAULT',
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        valid_types = {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}
        
        return obj and obj.mode != 'EDIT' and obj.type in valid_types
    
    def execute(self, context):
        shape_key_add(self.type)
        return {'FINISHED'}


class OBJECT_OT_skp_shape_key_remove(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_remove'
    bl_label = "Remove Shape Key"
    bl_description = "Remove shape key from the object"
    bl_options = {'REGISTER', 'UNDO'}
    
    type : bpy.props.EnumProperty(
        items=(
            ('DEFAULT', "", ""),
            ('CLEAR', "", ""),
            ('DEFAULT_SELECTED', "", "")
        ),
        default='DEFAULT',
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.mode != 'EDIT' and obj.active_shape_key
    
    def execute(self, context):
        shape_key_remove(self.type)
        return {'FINISHED'}


class OBJECT_OT_skp_shape_key_copy(bpy.types.Operator):
    bl_label = "Copy Shape"
    bl_idname = 'object.skp_shape_key_copy'
    bl_description = "Copy existing shape key"
    bl_options = {'REGISTER', 'UNDO'}
    
    type : bpy.props.EnumProperty(
        items=(
            ('DEFAULT', "", ""),
            ('MIRROR', "", ""),
            ('MIRROR_TOPOLOGY', "", ""),
            ('DEFAULT_SELECTED', "", ""),
            ('MIRROR_SELECTED', "", ""),
            ('MIRROR_TOPOLOGY_SELECTED', "", "")
        ),
        default='DEFAULT',
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key and obj.mode != 'EDIT'
    
    def execute(self, context):
        shape_key_copy(self.type)
        return {'FINISHED'}


class OBJECT_OT_skp_shape_key_move(bpy.types.Operator):
    bl_idname = 'object.skp_shape_key_move'
    bl_label = "Move Shape Key"
    bl_description = "Move shape key up/down in the list"
    bl_options = {'REGISTER', 'UNDO'}
    
    type : bpy.props.EnumProperty(
        name='Type',
        items=(
            ('TOP', "Top", ""),
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('BOTTOM', "Bottom", ""),
        ))
    
    selected : bpy.props.BoolProperty(
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        # Check if sibling shape keys exist before attempting to move.
        # A folder's children do not count as siblings to the folder.
        obj = context.object
        
        if not obj or obj.mode == 'EDIT':
            return False
        
        if obj.active_shape_key:
            # key_blocks will exist if active_shape_key exists.
            shape_keys = obj.data.shape_keys
            key_blocks = shape_keys.key_blocks
            basis_capacity = utils.get_folder_capacity(key_blocks[0])
            active_index = obj.active_shape_key_index
            
            return basis_capacity + 1 < len(key_blocks) or active_index > 0
        else:
            return False
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        
        if self.selected:
            original_name = obj.active_shape_key.name
            
            names = [key.name for key in utils.selected_shape_keys()]
            selections = [key.name for key in utils.selected_shape_keys()]
            
            shape_keys.shape_keys_plus.selections.clear()
            
            if self.type in ('DOWN', 'TOP'):
                selections = reversed(selections)
            
            for name in selections:
                index = utils.get_key_index(key_blocks[name])
                shape_key_move(self.type, index)
            
            for name in names:
                shape_key_select(name, True)
            
            original_index = key_blocks.find(original_name)
            obj.active_shape_key_index = original_index
        else:
            shape_key_move(self.type)
        
        return {'FINISHED'}


class OBJECT_OT_skp_shape_key_select(bpy.types.Operator):
    bl_label = "Select/Deselect Shape Key"
    bl_idname = 'object.skp_shape_key_select'
    bl_description = "Select this shape key"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode : bpy.props.EnumProperty(
        items=(
            ('TOGGLE', "", ""),
            ('ALL', "", ""),
            ('NONE', "", ""),
            ('INVERSE', "", "")
        ),
        options={'HIDDEN'})
    
    index : bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key
    
    def execute(self, context):
        skp = context.scene.shape_keys_plus
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        selections = shape_keys.shape_keys_plus.selections
        
        if self.mode == 'TOGGLE':
            shape_key_select(self.index, str(self.index) not in selections)
        elif self.mode == 'ALL':
            for index, key in enumerate(key_blocks):
                shape_key_select(index, True)
        elif self.mode == 'NONE':
            selections.clear()
        elif self.mode == 'INVERSE':
            for index, key in enumerate(key_blocks):
                shape_key_select(index, str(index) not in selections)
        
        return {'FINISHED'}


class OBJECT_OT_skp_folder_toggle(bpy.types.Operator):
    bl_label = "Expand/Collapse"
    bl_idname = 'object.skp_folder_toggle'
    bl_description = "Show or hide this folder's children"
    bl_options = {'REGISTER', 'UNDO'}
    
    index : bpy.props.IntProperty(options={'HIDDEN'})
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        active_key = obj.active_shape_key
        active_parents = utils.get_key_parents(active_key)
        folder = key_blocks[self.index]
        
        if folder in active_parents:
            # The active index shouldn't be on a hidden shape key.
            obj.active_shape_key_index = self.index
        
        utils.toggle_folder(folder)
        
        return {'FINISHED'}


class OBJECT_OT_skp_folder_ungroup(bpy.types.Operator):
    bl_label = "Ungroup Folder"
    bl_idname = 'object.skp_folder_ungroup'
    bl_description = "Ungroup this folder"
    bl_options = {'REGISTER', 'UNDO'}
    
    index : bpy.props.IntProperty(options={'HIDDEN'})
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key = shape_keys.key_blocks[self.index]
        is_folder = utils.is_key_folder(key)
        children = utils.get_folder_children(key)
        parent = utils.get_key_parent(key)
        
        selections = [key.name for key in utils.selected_shape_keys()]
        
        shape_keys.shape_keys_plus.selections.clear()
        
        utils.toggle_folder(key, expand=True)
        
        old_index = obj.active_shape_key_index
        
        if parent:
            utils.shift_folder_children_value(parent, utils.get_folder_children_value(key) - 1)
        
        for c in children:
            if utils.is_key_folder(c):
                utils.shift_folder_stack_value(c, -1)
        
        obj.active_shape_key_index = self.index
        bpy.ops.object.shape_key_remove()
        
        # Fix the active index.
        obj.active_shape_key_index = old_index - (1 if (old_index > self.index or not children) else 0)
        
        for name in selections:
            shape_key_select(name, True)
        
        return {'FINISHED'}


class DRIVER_OT_skp_driver_update(bpy.types.Operator):
    bl_label = "Update Driver"
    bl_idname = 'driver.skp_driver_update'
    bl_description = "Force update this driver"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if active_key:
            utils.update_driver(utils.get_key_driver(shape_keys, active_key))
        
        return {'FINISHED'}


class DRIVER_OT_skp_variable_add(bpy.types.Operator):
    bl_label = "Add Input Variable"
    bl_idname = 'driver.skp_variable_add'
    bl_description = "Add a new variable for this driver"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if active_key:
            driver = utils.get_key_driver(shape_keys, active_key)
            
            if driver:
                driver.variables.new()
        
        return {'FINISHED'}


class DRIVER_OT_skp_variable_remove(bpy.types.Operator):
    bl_label = "Remove Variable"
    bl_idname = 'driver.skp_variable_remove'
    bl_description = "Remove variable from the driver"
    bl_options = {'REGISTER', 'UNDO'}
    
    index : bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if active_key:
            driver = utils.get_key_driver(shape_keys, active_key)
            
            if driver and len(driver.variables) > self.index:
                driver.variables.remove(driver.variables[self.index])
        
        return {'FINISHED'}


class DRIVER_OT_skp_variable_copy(bpy.types.Operator):
    bl_label = "Copy Variable"
    bl_idname = 'driver.skp_variable_copy'
    bl_description = "Copy this variable"
    bl_options = {'REGISTER', 'UNDO'}
    
    index : bpy.props.IntProperty(options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if active_key:
            driver = utils.get_key_driver(shape_keys, active_key)
            
            if driver and len(driver.variables) > self.index:
                var = driver.variables.new()
                vars = list(driver.variables)
                
                vars.insert(self.index + 1, vars.pop(len(vars) - 1))
                
                var.name = vars[self.index].name + "_copy"
                var.type = vars[self.index].type
                
                for t in range(len(vars[self.index].targets)):
                    var.targets[t].bone_target = vars[self.index].targets[t].bone_target
                    var.targets[t].data_path = vars[self.index].targets[t].data_path
                    
                    if var.type == 'SINGLE_PROP':
                        var.targets[t].id_type = vars[self.index].targets[t].id_type
                    
                    var.targets[t].id = vars[self.index].targets[t].id
                    var.targets[t].transform_space = vars[self.index].targets[t].transform_space
                    var.targets[t].transform_type = vars[self.index].targets[t].transform_type
                
                utils.reconstruct_driver_variables(driver, vars)
        
        return {'FINISHED'}


class DRIVER_OT_skp_variable_move(bpy.types.Operator):
    bl_label = "Move Variable"
    bl_idname = 'driver.skp_variable_move'
    bl_description = "Move this variable up/down in the list"
    bl_options = {'REGISTER', 'UNDO'}
    
    index : bpy.props.IntProperty(options={'HIDDEN'})
    
    type : bpy.props.EnumProperty(
        items=(
            ('TOP', "", ""),
            ('UP', "", ""),
            ('DOWN', "", ""),
            ('BOTTOM', "", "")
        ),
        options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if active_key:
            driver = utils.get_key_driver(shape_keys, active_key)
            
            if driver and len(driver.variables) > self.index:
                vars = list(driver.variables)
                
                if self.type == 'TOP':
                    vars.insert(0, vars.pop(self.index))
                elif self.type == 'UP' and self.index > 0:
                    vars.insert(self.index - 1, vars.pop(self.index))
                elif self.type == 'DOWN' and self.index < len(vars) - 1:
                    vars.insert(self.index + 1, vars.pop(self.index))
                elif self.type == 'BOTTOM':
                    vars.insert(len(vars) - 1, vars.pop(self.index))
                
                utils.reconstruct_driver_variables(driver, vars)
        
        return {'FINISHED'}


class OBJECT_OT_skp_debug_folder_data(bpy.types.Operator):
    bl_label = "[ DEBUG ] Folder Data"
    bl_idname = 'object.skp_debug_folder_data'
    bl_description = "Manually create folder data"
    bl_options = {'REGISTER', 'UNDO'}
    
    folder : bpy.props.IntProperty(
        name="Folder Iterations",
        default=1,
        description="Number of times to indent the folder's children (1 + [number of folder's parents])")
    
    children : bpy.props.IntProperty(
        name="Children",
        default=0,
        description="The amount of children the folder has, not including children of children")
    
    expand : bpy.props.BoolProperty(
        name="Expand",
        default=True,
        description="Expand or collapse the folder")
    
    icons : bpy.props.IntProperty(
        name="Icon Pair",
        default=0,
        min=0,
        max=utils.icon_pairs[-1][-1],
        description="The pair of icons used when the folder is expanded or collapsed")
    
    icons_swap : bpy.props.BoolProperty(
        name="Swap Icons",
        default=False,
        description="Swap the icons used for when the folder is expanded or collapsed")
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_shape_key
    
    def execute(self, context):
        obj = context.object
        active_key = obj.active_shape_key
        
        active_key.vertex_group = utils.create_folder_data(
            folder=self.folder,
            children=self.children,
            expand=1 if self.expand else 0,
            icons=self.icons,
            icons_swap=1 if self.icons_swap else 0)
        
        return {'FINISHED'}


########################################################################
################################ PANEL #################################
########################################################################


class DATA_PT_shape_keys_plus(bpy.types.Panel):
    bl_label = "Shape Keys+"
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
        
        skp = context.scene.shape_keys_plus
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        active_index = obj.active_shape_key_index
        selections = utils.selected_shape_keys()
        
        if active_key:
            is_active_folder = utils.is_key_folder(active_key)
        else:
            is_active_folder = False
        
        enable_edit = obj.mode != 'EDIT'
        enable_edit_value = False
        
        if obj.show_only_shape_key is False:
            use_edit_mode = obj.type == 'MESH' and obj.use_shape_key_edit_mode
            
            if enable_edit or use_edit_mode:
                enable_edit_value = True
        
        row = layout.row()
        box = row.box()
        col = box.column()
        col.label(
            text="Placement",
            icon='NLA_PUSHDOWN')
        col.separator()
        
        prop_data = skp.bl_rna.properties['shape_key_add_placement']
        
        col.prop_menu_enum(
            data=skp,
            property='shape_key_add_placement',
            text="Add / Copy",
            icon=prop_data.enum_items[skp.shape_key_add_placement].icon)
        
        prop_data = skp.bl_rna.properties['shape_key_parent_placement']
        
        col.prop_menu_enum(
            data=skp,
            property='shape_key_parent_placement',
            text="Parent",
            icon=prop_data.enum_items[skp.shape_key_parent_placement].icon)
        
        prop_data = skp.bl_rna.properties['shape_key_unparent_placement']
        
        col.prop_menu_enum(
            data=skp,
            property='shape_key_unparent_placement',
            text="Unparent",
            icon=prop_data.enum_items[skp.shape_key_unparent_placement].icon)
        
        box = row.box()
        col = box.column()
        col.label(
            text="Hierarchy",
            icon='OUTLINER')
        col.separator()
        
        col.prop(
            data=skp,
            property='shape_key_auto_parent',
            toggle=True,
            icon='FILE_PARENT')
        
        col.prop(
            data=skp,
            property='shape_key_indent_scale',
            slider=True)
        
        box = row.box()
        box.scale_x = 0.75
        col = box.column()
        
        if selections:
            col.label(text=str(len(selections)) + " Selected")
        else:
            col.label(
                text="Select...",
                icon='RESTRICT_SELECT_OFF')
        
        col.separator()
        
        op = col.operator(
            operator='object.skp_shape_key_select',
            text="All",
            icon='ADD')
        
        op.mode = 'ALL'
        
        op = col.operator(
            operator='object.skp_shape_key_select',
            text="None",
            icon='REMOVE')
        
        op.mode = 'NONE'
        
        op = col.operator(
            operator='object.skp_shape_key_select',
            text="Inv.",
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
        
        col = row.column()
        
        #####################
        ######## ADD ########
        #####################
        
        row = col.row(align=True)
        btn = row.column()
        
        btn.enabled = not selections
        
        op = btn.operator(
            operator='object.skp_shape_key_add',
            icon='ADD',
            text="")
        
        op.type = 'DEFAULT'
        
        mnu = row.column()
        
        mnu.menu(
            menu='MESH_MT_skp_shape_key_add_specials',
            icon='DOWNARROW_HLT',
            text="")
        
        ######################
        ######## COPY ########
        ######################
        
        row = col.row(align=True)
        btn = row.column()
        
        btn.enabled = not selections
        
        op = btn.operator(
            operator='object.skp_shape_key_copy',
            icon='PASTEDOWN',
            text="")
        
        op.type = 'DEFAULT'
        
        mnu = row.column()
        
        mnu.menu(
            menu='MESH_MT_skp_shape_key_copy_specials',
            icon='DOWNARROW_HLT',
            text="")
        
        ########################
        ######## REMOVE ########
        ########################
        
        row = col.row(align=True)
        btn = row.column()
        
        btn.enabled = not selections
        
        op = btn.operator(
            operator='object.skp_shape_key_remove',
            icon='REMOVE',
            text="")
        
        op.type = 'DEFAULT'
        
        mnu = row.column()
        
        mnu.menu(
            menu='MESH_MT_skp_shape_key_remove_specials',
            icon='DOWNARROW_HLT',
            text="")
        
        #########################
        ######## SPECIAL ########
        #########################
        
        row = col.row(align=False)
        
        row.menu(
            menu='MESH_MT_skp_shape_key_other_specials',
            icon='DOWNARROW_HLT',
            text="")
        
        row.scale_x = 2.0
        
        if not active_key:
            return
        
        col.separator()
        
        sub = col.column(align=True)
        
        op = sub.operator(
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
        
        op = sub.operator(
            operator='object.skp_shape_key_move',
            icon='TRIA_DOWN_BAR',
            text="")
        
        op.type = 'BOTTOM'
        op.selected = bool(selections)
        
        split = layout.split(factor=0.4, align=False)
        
        row = split.row()
        row.enabled = enable_edit
        
        row.prop(
            data=shape_keys,
            property='use_relative')
        
        row = split.row()
        row.alignment = 'RIGHT'
        
        sub = row.row(align=True)
        sub.label()
        
        sub = sub.row(align=True)
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
                    text="Range:")
                
                col.prop(
                    data=active_key,
                    property='slider_min',
                    text="Min")
                
                col.prop(
                    data=active_key,
                    property='slider_max',
                    text="Max")
                
                col = split.column(align=True)
                col.active = enable_edit_value
                
                col.label(
                    text="Blend:")
                
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
        
        driver = utils.get_key_driver(shape_keys, active_key)
        
        if not driver:
            return
        
        layout.separator()
        
        row = layout.row()
        row.prop(
            data=skp,
            property='driver_visible')
        
        if not skp.driver_visible:
            return
        
        row = layout.row()
        row.label(text="Type:")
        
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
            row.label(text="Expression:")
            
            row = row.row()
            row.prop(
                data=driver,
                property='expression',
                text="")
            
            row.scale_x = 4
        
        row = layout.row(align=True)
        
        row.operator(
            operator='driver.skp_variable_add',
            icon='ADD')
        
        row.operator(
            operator='driver.skp_driver_update',
            icon='FILE_REFRESH')
        
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
                    text="Object",
                    expand=True)
                
                if target and target.id and target.id.type == 'ARMATURE':
                    col.prop_search(
                        data=target,
                        property='bone_target',
                        search_data=target.id.data,
                        search_property='bones',
                        text="Bone",
                        icon='BONE_DATA')
                
                row = box.row()
                col = row.column(align=True)
                
                col.prop(
                    data=driver.variables[i].targets[0],
                    property='transform_type',
                    text="Type")

                col.prop(
                    data=driver.variables[i].targets[0],
                    property='rotation_mode',
                    text="Mode")
                
                col.prop(
                    data=driver.variables[i].targets[0],
                    property='transform_space',
                    text="Space")
            elif driver.variables[i].type == 'ROTATION_DIFF':
                for i, target in enumerate(driver.variables[i].targets):
                    col = box.column(align=True)
                    
                    col.prop(
                        data=target,
                        property='id',
                        text="Object " + str(i + 1),
                        expand=True)
                    
                    if target.id and target.id.type == 'ARMATURE':
                        col.prop_search(
                            data=target,
                            property='bone_target',
                            search_data=target.id.data,
                            search_property='bones',
                            text="Bone",
                            icon='BONE_DATA')
                    
                    col = box.column(align=True)
                    
                    col.prop(
                        data=target,
                        property='transform_type',
                        text="Type")

                    col.prop(
                        data=target,
                        property='rotation_mode',
                        text="Mode")
                    
                    col.prop(
                        data=target,
                        property='transform_space',
                        text="Space")
            elif driver.variables[i].type == 'LOC_DIFF':
                for i, target in enumerate(driver.variables[i].targets):
                    row = box.column()
                    col = row.column(align=True)
                    
                    col.prop(
                        data=target,
                        property='id',
                        text="Object " + str(i + 1),
                        expand=True)
                    
                    if target.id and target.id.type == 'ARMATURE':
                        col.prop_search(
                            data=target,
                            property='bone_target',
                            search_data=target.id.data,
                            search_property='bones',
                            text="Bone",
                            icon='BONE_DATA')
                    
                    col.prop(
                        data=target,
                        property='transform_space',
                        text="Space")


class MESH_UL_shape_keys_plus(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        skp = context.scene.shape_keys_plus
        obj = active_data
        shape_keys = obj.data.shape_keys
        key_blocks = shape_keys.key_blocks
        key_block = item
        
        parents = utils.update_cache()['parents'][index]
        parent = get(parents, 0, None)
        is_folder = utils.is_key_folder(key_block)
        is_selected = utils.shape_key_selected(index)
        selections = utils.selected_shape_keys()
        
        use_edit_mode = obj.use_shape_key_edit_mode and obj.type == 'MESH'
        
        l1 = layout.row(align=True)
        l1.scale_x = 0.5
        
        # Check if this shape key belongs to a folder.
        if parent:
            # Get the number of folders this shape key is stacked in.
            for _ in range(utils.get_folder_stack_value(parent)):
                # Use the customizable folder indentation.
                for _ in range(skp.shape_key_indent_scale):
                    l1.separator(factor=2)
        
        if is_folder:
            icon_pair_value = utils.block_value(key_block.vertex_group, utils.icons)
            icon_swap_value = utils.block_value(key_block.vertex_group, utils.icons_swap)
            expand_value = utils.block_value(key_block.vertex_group, utils.expand)
            icon_pair = utils.get_icon_pair(icon_pair_value)
            icon_swap = icon_swap_value == 1
            
            if expand_value > 0:
                icon = icon_pair[1 if icon_swap else 0]
            else:
                icon = icon_pair[0 if icon_swap else 1]
            
            # Align the folder toggle button with the shape key icons.
            l1.separator(factor=3)
            
            op = l1.operator(
                operator='object.skp_folder_toggle',
                text="",
                icon=icon,
                emboss=False)
            
            op.index = index
            
            l2 = l1.row(align=True)
            l2.scale_x = 2
            l2.separator(factor=0.5)
            
            l2.prop(
                data=key_block,
                property='name',
                text="",
                emboss=False)
        else:
            l2 = l1.row()
            l2.scale_x = 2
            l2.active = not selections or is_selected
            
            l2.prop(
                data=key_block,
                property='name',
                text="",
                emboss=False,
                icon='FILE_TICK' if is_selected else 'SHAPEKEY_DATA')
        
        row = layout.row(align=True)
        
        if is_folder:
            if key_block.mute or (obj.mode == 'EDIT' and not use_edit_mode):
                row.active = False
            
            op = row.operator(
                operator='object.skp_folder_ungroup',
                text="",
                icon='X',
                emboss=False)
            
            op.index = index
        else:
            if key_block.mute or (obj.mode == 'EDIT' and not use_edit_mode):
                row.active = False
            if not item.id_data.use_relative:
                row.prop(
                    data=key_block,
                    property='frame',
                    text="",
                    emboss=False)
            elif index > 0:
                can_edit = not selections or selections and is_selected
                
                if can_edit:
                    row.prop(
                        data=key_block,
                        property='value',
                        text="",
                        emboss=False)
                else:
                    row.active = False
                    row.alignment = 'RIGHT'
                    row.label(text='{0:.3f}'.format(key_block.value))
            
            row.prop(
                data=key_block,
                property='mute',
                text="",
                icon='HIDE_OFF',
                emboss=False)
            
            if index > 0 and not is_folder:
                op = row.operator(
                    operator='object.skp_shape_key_select',
                    text="",
                    icon='CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT',
                    emboss=False)
                
                op.index = index
                op.mode = 'TOGGLE'
    
    def draw_filter(self, context, layout):
        skp = context.scene.shape_keys_plus
        
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
            data=skp,
            property='show_filtered_folder_contents',
            text="",
            icon=icon)
        
        subrow = row.row(align=True)
        
        icon = 'HIDE_OFF'
        
        subrow.prop(
            data=skp,
            property='shape_key_limit_to_active',
            text="",
            icon=icon)
        
        if skp.shape_key_limit_to_active:
            subrow.prop(
                data=skp,
                property='filter_active_threshold',
                text="")
            
            icon = 'TRIA_LEFT' if skp.filter_active_below else 'TRIA_RIGHT'
            
            subrow.prop(
                data=skp,
                property='filter_active_below',
                text="",
                icon=icon)
    
    def filter_items(self, context, data, propname):
        flt_flags = []
        flt_name_flags = []
        flt_neworder = []
        
        skp = context.scene.shape_keys_plus
        shape_keys = context.object.data.shape_keys
        key_blocks = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        filtering_by_name = False
        name_filters = [False] * len(key_blocks)
        
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
            cache = utils.update_cache()
            parents = cache['parents'][idx]
            is_folder = utils.is_key_folder(key)
            
            hidden = False
            
            if parents:
                parent_collapsed = False
                
                for p in parents:
                    expand_value = utils.block_value(
                        p.vertex_group,
                        utils.expand)
                    
                    if expand_value == 0:
                        parent_collapsed = True
                        break
                
                if parent_collapsed and not filtering_by_name:
                    hidden = True
            
            if hidden:
                filter_set(idx, False)
            
            if filtering_by_name and parents:
                for p in parents:
                    parent_index = utils.get_key_index(p)
                    parent_hidden = not name_filters[parent_index]
                    
                    if name_filters[idx] and parent_hidden:
                        filter_set(parent_index, True)
            
            if skp.show_filtered_folder_contents:
                if is_folder and filter_get(idx):
                    children = cache['children'][idx]
                    
                    for i in range(len(children)):
                        filter_set(idx + 1 + i, True)
            
            if skp.shape_key_limit_to_active:
                if is_folder:
                    filter_set(idx, False)
                else:
                    val = skp.filter_active_threshold
                    below = skp.filter_active_below
                    
                    in_active_range = \
                        key.value <= val if \
                        below else \
                        key.value >= val
                    
                    filter_set(idx, in_active_range)
        
        return flt_flags, flt_neworder


########################################################################
############################# REGISTRATION #############################
########################################################################


classes = (
    AddonProperties,
    Selection,
    KeyProperties,
    SceneProperties,
    
    MESH_MT_skp_shape_key_add_specials,
    MESH_MT_skp_shape_key_add_specials_selected,
    MESH_MT_skp_shape_key_copy_specials,
    MESH_MT_skp_shape_key_copy_specials_selected,
    MESH_MT_skp_shape_key_remove_specials,
    MESH_MT_skp_shape_key_remove_specials_selected,
    MESH_MT_skp_shape_key_other_specials,
    MESH_MT_skp_shape_key_other_specials_selected,
    OBJECT_MT_skp_shape_key_parent,
    OBJECT_MT_skp_shape_key_parent_selected,
    OBJECT_MT_skp_folder_icon,
    OBJECT_MT_skp_folder_icons_standard,
    OBJECT_MT_skp_folder_icons_special,
    OBJECT_MT_skp_folder_icons_misc,
    
    OBJECT_OT_skp_folder_icon,
    OBJECT_OT_skp_shape_key_parent,
    OBJECT_OT_skp_shape_key_add,
    OBJECT_OT_skp_shape_key_remove,
    OBJECT_OT_skp_shape_key_copy,
    OBJECT_OT_skp_shape_key_move,
    OBJECT_OT_skp_shape_key_select,
    OBJECT_OT_skp_folder_toggle,
    OBJECT_OT_skp_folder_ungroup,
    DRIVER_OT_skp_driver_update,
    DRIVER_OT_skp_variable_add,
    DRIVER_OT_skp_variable_remove,
    DRIVER_OT_skp_variable_copy,
    DRIVER_OT_skp_variable_move,
    OBJECT_OT_skp_debug_folder_data,
    
    DATA_PT_shape_keys_plus,
    MESH_UL_shape_keys_plus
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.shape_keys_plus = bpy.props.PointerProperty(type=SceneProperties)
    bpy.types.Key.shape_keys_plus = bpy.props.PointerProperty(type=KeyProperties)
    
    if __name__ != "__main__":
        preferences = bpy.context.preferences.addons[__name__].preferences
        
        default_panel_exists = hasattr(bpy.types, 'DATA_PT_shape_keys')
        
        if preferences.hide_default and default_panel_exists:
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


if __name__ == "__main__":
    register()
