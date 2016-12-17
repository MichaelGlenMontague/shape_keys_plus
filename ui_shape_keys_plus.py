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
    "name": "Shape Keys+",
    "author": "Michael Glen Montague",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "location": "Properties > Data",
    "description": "Adds a panel with extra options for creating, sorting, viewing, and driving shape keys.",
    "warning": "",
    "wiki_url": "",
    "category": "Object"
}

import bpy
import re

#################################################################################################
############################################ CLASSES ############################################
#################################################################################################

class ShapeKeysPlusPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    enable_debugging = bpy.props.BoolProperty(name = "Enable Debugging", default = False, description = "Enables unstable operations for debugging")
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        
        row.prop(self, "enable_debugging")

class SKP():
    prefix = "SKP"
    folder = ".F"
    children = ".C"
    expand = ".E"
    icons = ".I"
    icons_swap = ".IS"
    
    folder_default = 1 # this value will be given to all children as the parent count
    children_default = 0 # number of shape keys under the folder
    expand_default = 1 # 0 = collapse, 1 = expand
    icons_swap_default = 0 # 0 = normal, 1 = swap
    
    #icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
    
    icon_pairs = [
        ("DISCLOSURE_TRI_DOWN", "DISCLOSURE_TRI_RIGHT", "Outliner"),
        ("TRIA_DOWN", "TRIA_RIGHT", "White"),
        ("DISCLOSURE_TRI_DOWN_VEC", "DISCLOSURE_TRI_RIGHT_VEC", "Gray"),
        ("DOWNARROW_HLT", "RIGHTARROW", "Black"),
        ("FILESEL", "FILE_FOLDER", "Folder"),
        ("PACKAGE", "UGLYPACKAGE", "Package"),
        ("LAYER_ACTIVE", "LAYER_USED", "Layer"),
        ("SPACE2", "SPACE3", "Keyframe"),
        ("KEY_HLT", "KEY_DEHLT", "Key"),
        ("MARKER_HLT", "MARKER", "Marker"),
        ("PMARKER_ACT", "PMARKER", "Diamond"),
        ("RADIOBUT_ON", "RADIOBUT_OFF", "Bullet"),
        ("CHECKBOX_HLT", "CHECKBOX_DEHLT", "Checkbox"),
        ("UNPINNED", "PINNED", "Pin"),
        ("DOT", "LINK", "Dot"),
        ("PROP_ON", "PROP_OFF", "Proportional"),
        ("ZOOM_OUT", "ZOOM_IN", "Magnifier"),
        ("INLINK", "LINK", "Donut"),
        ("LAMP_SUN", "FREEZE", "Temperature"),
        ("PARTICLE_DATA", "MOD_PARTICLES", "Magic"),
        ("AUTOMERGE_ON", "AUTOMERGE_OFF", "Merge"),
        ("UNLOCKED", "LOCKED", "Lock"),
        ("SNAP_ON", "SNAP_OFF", "Magnet"),
        ("MONKEY", "MOD_MASK", "Monkey"),
        ("WORLD", "MATSPHERE", "World"),
        ("OBJECT_DATA", "MESH_CUBE", "Object"),
        ("NODE_SEL", "NODE", "Node"),
        ("NODE_INSERT_OFF", "NODE_INSERT_ON", "Nodes"),
        ("SMOOTHCURVE", "SPHERECURVE", "Squeeze"),
        ("SHARPCURVE", "ROOTCURVE", "Pinch"),
        ("RNDCURVE", "NOCURVE", "Noise"),
        ("RESTRICT_RENDER_OFF", "RESTRICT_RENDER_ON", "Camera"),
        ("RESTRICT_SELECT_OFF", "RESTRICT_SELECT_ON", "Cursor"),
        ("RESTRICT_VIEW_OFF", "RESTRICT_VIEW_ON", "Eye"),
        ("SOLO_ON", "SOLO_OFF", "Star"),
        ("OUTLINER_OB_EMPTY", "OUTLINER_DATA_EMPTY", "Empty"),
        ("OUTLINER_OB_EMPTY", "OUTLINER_DATA_EMPTY", "Mesh"),
        ("OUTLINER_OB_CURVE", "OUTLINER_DATA_CURVE", "Curve"),
        ("OUTLINER_OB_LATTICE", "OUTLINER_DATA_LATTICE", "Lattice"),
        ("OUTLINER_OB_META", "BONE_DATA", "Metaball"),
        ("OUTLINER_OB_LAMP", "OUTLINER_DATA_LAMP", "Lamp"),
        ("OUTLINER_OB_CAMERA", "OUTLINER_DATA_CAMERA", "Film"),
        ("OUTLINER_OB_ARMATURE", "ARMATURE_DATA", "Human"),
        ("MOD_ARMATURE", "POSE_DATA", "Blueman"),
        ("POSE_HLT", "OUTLINER_DATA_POSE", "Truman"),
        ("OUTLINER_OB_FONT", "FONT_DATA", "Font"),
        ("OUTLINER_OB_SURFACE", "OUTLINER_DATA_SURFACE", "Surface"),
        ("OUTLINER_OB_SPEAKER", "OUTLINER_DATA_SPEAKER", "Speaker"),
        ("PLAY_AUDIO", "MUTE_IPO_ON", "Mute"),
        ("COLOR_RED", "COLOR", "Red"),
        ("COLOR_GREEN", "COLOR", "Green"),
        ("COLOR_BLUE", "COLOR", "Blue"),
        ("GHOST_ENABLED", "GHOST_DISABLED", "Ghost"),
        ("COLLAPSEMENU", "GRIP", "Lines"),
        ("STICKY_UVS_DISABLE", "GROUP_VERTEX", "Points"),
        ("STICKY_UVS_VERT", "STICKY_UVS_LOC", "Pressure"),
        ("FILE_BLANK", "FILE_HIDDEN", "Paper"),
        ("LIBRARY_DATA_DIRECT", "LIBRARY_DATA_INDIRECT", "Direct"),
        ("SYNTAX_ON", "SYNTAX_OFF", "Alpha"),
        ("UNLINKED", "LINKED", "Link"),
        ("CONSTRAINT_DATA", "CONSTRAINT", "Chain"),
    ]
    
    all_data = {"pointers" : [], "parents" : [], "children" : []}
    
    @staticmethod
    def data(override = False):
        obj = bpy.context.active_object
        
        if obj is not None:
            shape_keys = obj.data.shape_keys
            if shape_keys is not None:
                keys = [kb.as_pointer() for kb in shape_keys.key_blocks]
                
                if SKP.all_data["pointers"] != keys or override:
                    SKP.all_data["pointers"] = keys
                    SKP.all_data["parents"].clear()
                    SKP.all_data["children"].clear()
                    for kb in shape_keys.key_blocks:
                        SKP.all_data["parents"].append(SKP.get_key_parents(kb))
                        SKP.all_data["children"].append(SKP.get_folder_children(kb))
        
        return SKP.all_data
    
    @staticmethod
    def create_folder_data(
            folder = folder_default,
            children = children_default,
            expand = expand_default,
            icons = None,
            icons_swap = icons_swap):
        
        if folder is None:
            folder = folder_default
        if children is None:
            children = children_default
        if expand is None:
            expand = expand_default
        if icons is None:
            icons = bpy.context.scene.skp_folder_icon_pair
        if icons_swap is None:
            icons_swap = icons_swap_default
        
        skp = SKP.prefix
        folder = SKP.folder + str(folder)
        children = SKP.children + str(children)
        expand = SKP.expand + str(expand)
        icons = SKP.icons + str(icons)
        icons_swap = SKP.icons_swap + str(icons_swap)
        
        return skp + folder + children + expand + icons + icons_swap
    
    @staticmethod
    def get_block(data, block = None):
        if data.startswith(SKP.prefix):
            if block is None:
                return data.split(".")
            else:
                data = data.split(".")
                block = re.sub(r"[^A-Za-z]", "", block)
                
                for x in data:
                    if block in x:
                        return x
        
        return None
    
    @staticmethod
    def has_block(data, block):
        return SKP.get_block(data, block) is not None
    
    @staticmethod
    def block_index(data, block):
        data = data.split(".")
        block = re.sub(r"[^A-Za-z]", "", block)
        for i, x in enumerate(data):
            if block in x:
                return i
    
    @staticmethod
    def block_set(data, block, value):
        if SKP.has_block(data, block):
            original = SKP.get_block(data, block)
            key = re.sub(r"[^A-Za-z]", "", original)
            
            split = data.split(".")
            index = SKP.block_index(data, block)
            
            split[index] = key + str(value)
            
            return ".".join(split)
        
        return data
    
    @staticmethod
    def block_value(data, block):
        if SKP.has_block(data, block):
            default = None
            
            if block == SKP.folder:
                default = SKP.folder_default
            elif block == SKP.children:
                default = SKP.children_default
            elif block == SKP.expand:
                default = SKP.expand_default
            elif block == SKP.icons:
                default = bpy.context.scene.skp_folder_icon_pair
            elif block == SKP.icons_swap:
                default = SKP.icons_swap_default
            
            if default is not None:
                value = re.sub(r"\D", "", SKP.get_block(data, block))
                
                if value != "":
                    return int(value)
                else:
                    return default
        
        return -1
    
    @staticmethod
    def is_key_folder(key):
        return SKP.has_block(key.vertex_group, SKP.folder)
    
    @staticmethod
    def get_folder_capacity(folder, context = None):
        if context is None:
            context = bpy.context
        
        capacity = 0
        
        if SKP.is_key_folder(folder):
            shape_keys = context.object.data.shape_keys
            folder_index = SKP.get_key_index(folder)
            
            s = folder_index + 1
            e = s + SKP.get_folder_children_value(folder)
            
            i = s
            
            while i < e:
                if len(shape_keys.key_blocks) > i:
                    key = shape_keys.key_blocks[i]
                    
                    capacity += 1
                    
                    if SKP.is_key_folder(key):
                        e += SKP.get_folder_children_value(key)
                    
                    i += 1
        
        return capacity
    
    @staticmethod
    def get_folder_children(folder, context = None):
        if context is None:
            context = bpy.context
        
        children = []
        
        if SKP.is_key_folder(folder):
            shape_keys = context.object.data.shape_keys
            folder_index = shape_keys.key_blocks.find(folder.name)
            index = folder_index + 1
            capacity = SKP.get_folder_children_value(folder)
            
            for i in range(index, index + SKP.get_folder_capacity(folder, context = context)):
                if len(shape_keys.key_blocks) > i:
                    children.append(shape_keys.key_blocks[i])
        
        return children
    
    @staticmethod
    def get_key_parent(key, context = None):
        if context is None:
            context = bpy.context
        
        if key is not None:
            shape_keys = context.object.data.shape_keys
            index = SKP.get_key_index(key)
            i = index - 1
            
            while i >= 0:
                key = shape_keys.key_blocks[i]
                is_folder = SKP.is_key_folder(key)
                capacity = SKP.get_folder_capacity(key)
                if is_folder and capacity > 0:
                    if i <= index <= i + capacity:
                        return key
                
                i -= 1
                
        return None
    
    @staticmethod
    def get_key_parents(key, context = None):
        if context is None:
            context = bpy.context
        
        parents = []
        
        if key is not None:
            shape_keys = context.object.data.shape_keys
            index = SKP.get_key_index(key)
            i = index - 1
            
            while i >= 0:
                key = shape_keys.key_blocks[i]
                is_folder = SKP.is_key_folder(key)
                capacity = SKP.get_folder_capacity(key)
                if is_folder and capacity > 0:
                    if i <= index <= i + capacity:
                        parents.append(key)
                        
                        if SKP.get_folder_stack_value(key) < 2:
                            break
                
                i -= 1
        
        return parents
    
    @staticmethod
    def get_key_index(key, context = None):
        if context is None:
            context = bpy.context
        
        if context.object is not None:
            if context.object.data.shape_keys is not None:
                return context.object.data.shape_keys.key_blocks.find(key.name)
        
        return -1
    
    @staticmethod
    def get_key_siblings(key):
        context = bpy.context
        shape_keys = context.object.data.shape_keys
        parents = SKP.get_key_parents(key)
        parent = parents[0] if len(parents) > 0 else None
        index = SKP.get_key_index(key)
        siblings = [None, None]
        
        previous_key = shape_keys.key_blocks[index - 1] if index - 1 >= 0 else None
        
        if SKP.is_key_folder(key):
            capacity = SKP.get_folder_capacity(key)
            next_key = shape_keys.key_blocks[index + capacity + 1] if index + capacity + 1 < len(shape_keys.key_blocks) else None
        else:
            next_key = shape_keys.key_blocks[index + 1] if index + 1 < len(shape_keys.key_blocks) else None
        
        if previous_key is not None:
            previous_key_parents = SKP.get_key_parents(previous_key)
            previous_key_parent = previous_key_parents[0] if len(previous_key_parents) > 0 else None
            
            if parent is not None:
                if previous_key_parent is not None:
                    if previous_key_parent.name == parent.name:
                        siblings[0] = previous_key
                    elif previous_key.name != parent.name:
                        siblings[0] = previous_key_parents[len(previous_key_parents) - len(parents) - 1]
            else:
                if previous_key_parent is not None:
                    siblings[0] = previous_key_parents[-1]
                else:
                    siblings[0] = previous_key
        
        if next_key is not None:
            next_key_parents = SKP.get_key_parents(next_key)
            next_key_parent = next_key_parents[0] if len(next_key_parents) > 0 else None
            
            if parent is not None:
                if next_key_parent is not None:
                    if next_key_parent.name == parent.name:
                        siblings[1] = next_key
            else:
                if next_key_parent is not None:
                    pass
                else:
                    siblings[1] = next_key
        
        return siblings
    
    @staticmethod
    def shift_folder_children_value(key, amount):
        if SKP.has_block(key.vertex_group, SKP.children):
            key.vertex_group = SKP.block_set(key.vertex_group, SKP.children, max(0, SKP.block_value(key.vertex_group, SKP.children) + amount))
    
    @staticmethod
    def shift_folder_stack_value(key, amount):
        if SKP.has_block(key.vertex_group, SKP.folder):
            key.vertex_group = SKP.block_set(key.vertex_group, SKP.folder, max(1, SKP.block_value(key.vertex_group, SKP.folder) + amount))
    
    @staticmethod
    def set_folder_children_value(key, val):
        if SKP.has_block(key.vertex_group, SKP.folder):
            key.vertex_group = SKP.block_set(key.vertex_group, SKP.children, val)
    
    @staticmethod
    def set_folder_stack_value(key, val):
        if SKP.has_block(key.vertex_group, SKP.folder):
            key.vertex_group = SKP.block_set(key.vertex_group, SKP.folder, val)
    
    @staticmethod
    def get_folder_children_value(key):
        return SKP.block_value(key.vertex_group, SKP.children)
    
    @staticmethod
    def get_folder_stack_value(key):
        return SKP.block_value(key.vertex_group, SKP.folder)
    
    @staticmethod
    def toggle_folder(key, expand = None):
        if SKP.is_key_folder(key):
            original = SKP.block_value(key.vertex_group, SKP.expand)
            
            if expand is None:
                toggle = 1 if original == 0 else 0
            else:
                toggle = 1 if expand else 0
            
            key.vertex_group = SKP.block_set(key.vertex_group, SKP.expand, toggle)
    
    @staticmethod
    def get_key_driver(shape_keys, key):
        anim = shape_keys.animation_data
        
        if exists(anim) and exists(anim.drivers):
            for fcu in anim.drivers:
                if fcu.data_path == ("key_blocks[\"" + key.name + "\"].value"):
                    return fcu.driver
        
        return None
    
    @staticmethod
    def update_driver(driver):
        if exists(driver):
            driver.expression += " "
            driver.expression = driver.expression[:-1]
    
    @staticmethod
    def refresh_driver_variables(driver, reference):
        driver_len = len(driver.variables)
        reference_len = len(reference)
        
        old_variables = {"name" : [], "targets" : [], "type" : []}
        
        '''def print_old_variables(index):
            print("Name: " + str(old_variables["name"][index]))
            print("Type: " + str(old_variables["type"][index]) + "\n")
            
            for i in range(old_variables["targets"][index]["count"]):
                print("Target " + str(i + 1) + ": ")
                print("\tBone Target: " + old_variables["targets"][index]["bone_target"][i])
                print("\tData Path: " + old_variables["targets"][index]["data_path"][i])
                print("\tID: " + (old_variables["targets"][index]["id"][i].name if old_variables["targets"][index]["id"][i] else ""))
                print("\tID Type: " + old_variables["targets"][index]["id_type"][i])
                print("\tTransform Space: " + old_variables["targets"][index]["transform_space"][i])
                print("\tTransform Type: " + old_variables["targets"][index]["transform_type"][i])'''
        
        for i in range(driver_len):
            old_variables["name"].append(reference[i].name)
            old_variables["type"].append(reference[i].type)
            old_variables["targets"].append({"count" : 0, "bone_target" : [], "data_path" : [], "id" : [], "id_type" : [], "transform_space" : [], "transform_type" : []})
            
            for t in range(len(reference[i].targets)):
                old_variables["targets"][i]["count"] = old_variables["targets"][i]["count"] + 1
                old_variables["targets"][i]["bone_target"].append(reference[i].targets[t].bone_target)
                old_variables["targets"][i]["data_path"].append(reference[i].targets[t].data_path)
                old_variables["targets"][i]["id"].append(reference[i].targets[t].id)
                old_variables["targets"][i]["id_type"].append(reference[i].targets[t].id_type)
                old_variables["targets"][i]["transform_space"].append(reference[i].targets[t].transform_space)
                old_variables["targets"][i]["transform_type"].append(reference[i].targets[t].transform_type)
                
        for i in range(driver_len):
            driver.variables.remove(driver.variables[driver_len - 1 - i])
        
        for i in range(reference_len):
            new_variable = driver.variables.new()
            
            new_variable.name = old_variables["name"][i]
            # the type controls the targets, so this comes first
            new_variable.type = old_variables["type"][i]
            
            for t in range(old_variables["targets"][i]["count"]):
                new_variable.targets[t].bone_target = old_variables["targets"][i]["bone_target"][t]
                new_variable.targets[t].data_path = old_variables["targets"][i]["data_path"][t]
                
                # only the "Single Property" type can have its ID Type changed to a non-object
                if new_variable.type == "SINGLE_PROP":
                    new_variable.targets[t].id_type = old_variables["targets"][i]["id_type"][t]
                
                new_variable.targets[t].id = old_variables["targets"][i]["id"][t]
                new_variable.targets[t].transform_space = old_variables["targets"][i]["transform_space"][t]
                new_variable.targets[t].transform_type = old_variables["targets"][i]["transform_type"][t]
        
        SKP.update_driver(driver)

class Metadata():
    key = None
    index = 0
    
    context = None
    parents = []
    children = []
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
    
    def __init__(self, key, index, context = None):
        self.key = key
        self.index = index
        
        if context is None:
            self.context = bpy.context
        
        self.parents = SKP.get_key_parents(self.key, context = self.context)
        self.children = SKP.get_folder_children(self.key, context = self.context)
        self.is_folder = SKP.is_key_folder(self.key)
        self.stack = len(self.parents)
        self.is_parented = self.stack > 0
        
        if self.is_parented:
            self.first_parent = self.parents[0]
            self.last_parent = self.parents[-1]
        
        self.capacity = len(self.children)
        self.has_children = self.capacity > 0
        
        if self.has_children:
            self.first_child = self.children[0]
            self.last_child = self.children[-1]
        
        shape_keys = context.object.data.shape_keys
        
        if shape_keys is not None:
            if self.has_children:
                self.first_child_index = shape_keys.key_blocks.find(self.first_child.name)
                self.last_child_index = shape_keys.key_blocks.find(self.last_child.name)
            
            if self.is_parented:
                folder = SKP.get_folder_children(self.parents[0], context = self.context)
                
                self.is_first_child = self.key.name == folder[0].name
                self.is_last_child = self.key.name == folder[-1].name
            
            self.previous_key = shape_keys.key_blocks[index - 1] if index > 0 else None
            self.next_key = shape_keys.key_blocks[index + self.capacity + 1] if len(shape_keys.key_blocks) > index + self.capacity + 1 else None
    
    def print_data(self):
        print("Key:", self.key.name)
        print("Index:", self.index)
        print("Parent:", self.parents[0].name if self.is_parented else "None")
        print("Is Folder:", self.is_folder)
        print("Children:", self.capacity if self.has_children else "None")
        for c in self.children:
            t = " "
            for x in (SKP.get_key_parents(c, context = self.context)):
                t += " "
            print(t + c.name)
        print("\n")
    
    def __eq__(self, other):
        if self is not None and other is not None:
            return self.key.name == other.key.name
        
        return False
    
    def __ne__(self, other):
        return not self == other

class Debug():
    @staticmethod
    def print_skp_data():
        data = skp_data()
        for d in data:
            d.print_data()

#################################################################################################
######################################## HELPER FUNCTIONS #######################################
#################################################################################################

def exists(x):
    return x is not None

def skp_data(context = None):
    if context is None:
        context = bpy.context
    
    data = []
    
    obj = context.object
    
    if exists(obj):
        shape_keys = obj.data.shape_keys
        if exists(shape_keys):
            for index, key in enumerate(shape_keys.key_blocks):
                data.append(Metadata(key = key, index = index, context = context))
    
    return data

def metadata(data, key):
    m = None
    
    for d in data:
        if d.key.name == key.name:
            m = d
            break
    
    return m

def shape_key_selected(index):
    return index in bpy.context.scene.skp_shape_key_selections and bpy.context.scene.skp_shape_key_selections[index]

def selected_shape_keys():
    return [s for s in bpy.context.scene.skp_shape_key_selections.values() if s == True]

def move_shape_key_direction(key, direction):
    bpy.context.object.active_shape_key_index = SKP.get_key_index(key)
    bpy.ops.object.shape_key_move(type = direction)

def move_folder_direction(folder, direction):
    obj = bpy.context.object
    index = SKP.get_key_index(folder)
    capacity = SKP.get_folder_capacity(folder)
    
    r = range(index, index + capacity + 1) if direction == "UP" else reversed(range(index, index + capacity + 1))
    
    for i in r:
        obj.active_shape_key_index = i
        bpy.ops.object.shape_key_move(type = direction)
        
    obj.active_shape_key_index = index - 1 if direction == "UP" else index + 1

def move_shape_key_to(origin, destination):
    obj = bpy.context.object
    shape_keys = obj.data.shape_keys
    key = shape_keys.key_blocks[origin]
    
    if SKP.is_key_folder(key):
        offset = 0
        
        if origin < destination:
            offset = -(SKP.get_folder_capacity(key) + 1)
        
        for _ in range(abs(origin - destination) + offset):
            if origin > destination:
                move_folder_direction(key, "UP")
            elif origin < destination:
                move_folder_direction(key, "DOWN")
    else:
        offset = 0
        
        if origin < destination:
            offset = -1
        
        for _ in range(abs(origin - destination) + offset):
            if origin > destination:
                move_shape_key_direction(key, "UP")
            elif origin < destination:
                move_shape_key_direction(key, "DOWN")

def fix_new_placement(reference, key, internal = False, reference_parent_capacity = None, offset = 0):
    context = bpy.context
    shape_keys = context.object.data.shape_keys
    key_index = shape_keys.key_blocks.find(key.name)
    reference_index = shape_keys.key_blocks.find(reference.name)
    
    reference_parents = SKP.get_key_parents(reference)
    reference_parent = reference_parents[0] if len(reference_parents) > 0 else None
    is_reference_folder = SKP.is_key_folder(reference)
    is_reference_parented = exists(reference_parent)
    
    if is_reference_folder:
        parent = reference
    elif is_reference_parented:
        parent = reference_parent
        
        if not exists(reference_parent_capacity): # same functionality as fix_parent_placement's capacity parameter
            reference_parent_capacity = SKP.get_folder_capacity(reference_parent)
    else:
        parent = None
    
    if context.scene.skp_shape_key_new_placement == "TOP":
        if not internal:
            first_index_capacity = SKP.get_folder_capacity(shape_keys.key_blocks[0])
            if first_index_capacity > 0:
                placement = first_index_capacity + 1
            else:
                placement = 1
        elif is_reference_parented:
            placement = SKP.get_key_index(reference_parent) + 1
    elif context.scene.skp_shape_key_new_placement == "ABOVE":
        if is_reference_parented and not internal:
            placement = SKP.get_key_index(reference_parents[-1])
        else:
            placement = reference_index
    elif context.scene.skp_shape_key_new_placement == "BELOW":
        if not internal:
            if is_reference_folder:
                r = reference_parents[-1] if len(reference_parents) > 0 else reference
                placement = SKP.get_key_index(r) + SKP.get_folder_capacity(r) + 1
            elif is_reference_parented:
                placement = SKP.get_key_index(reference_parents[-1]) + SKP.get_folder_capacity(reference_parents[-1]) + 1
            else:
                placement = reference_index + 1
        else:
            placement = reference_index + 1
    elif context.scene.skp_shape_key_new_placement == "BOTTOM":
        if not internal:
            placement = len(shape_keys.key_blocks) - 1
        elif is_reference_parented:
            placement = SKP.get_key_index(reference_parent) + reference_parent_capacity
    
    move_shape_key_to(origin = key_index, destination = placement + offset)

def fix_parent_placement(child, parent, capacity = None, offset = 0):
    context = bpy.context
    shape_keys = context.object.data.shape_keys
    child_index = SKP.get_key_index(child)
    parent_index = SKP.get_key_index(parent)
    
    if not exists(capacity):
        capacity = SKP.get_folder_capacity(parent)
    
    if context.scene.skp_shape_key_parent_placement == "TOP":
        placement = parent_index + 1
    elif context.scene.skp_shape_key_parent_placement == "BOTTOM":
        placement = parent_index + capacity
    
    move_shape_key_to(origin = child_index, destination = placement + offset)

def fix_unparent_placement(key):
    key_index = SKP.get_key_index(key)
    bpy.context.object.active_shape_key_index = key_index
    
    placement = bpy.context.scene.skp_shape_key_unparent_placement
    
    if placement == "TOP":
        if key_index > 1:
            bpy.ops.object.skp_shape_key_move(type = "TOP")
    elif placement == "ABOVE":
        pass
    elif placement == "BELOW":
        bpy.ops.object.skp_shape_key_move(type = "DOWN")
    elif placement == "BOTTOM":
        bpy.ops.object.skp_shape_key_move(type = "BOTTOM")

def fix_copy_placement(original, copy, original_parent_capacity = None, offset = 0):
    context = bpy.context
    shape_keys = context.object.data.shape_keys
    original_parents = SKP.get_key_parents(original)
    original_parent = original_parents[0] if len(original_parents) > 0 else None
    original_index = SKP.get_key_index(original)
    are_keys_folders = SKP.is_key_folder(original) and SKP.is_key_folder(copy)
    capacity = SKP.get_folder_capacity(original)
    
    original_parent_index = 0
    
    if exists(original_parent):
        original_parent_index = SKP.get_key_index(original_parent)
        
        if not exists(original_parent_capacity): # same functionality as fix_parent_placement's capacity parameter
            original_parent_capacity = SKP.get_folder_capacity(original_parents[0])
    
    
    if context.scene.skp_shape_key_new_placement == "TOP":
        if exists(original_parent) and context.scene.skp_shape_key_auto_parent:
            placement = original_parent_index + 1
        else:
            is_first_index = are_keys_folders and original_index == 0
            is_parented_to_first_index = exists(original_parent) and SKP.get_key_index(original_parents[-1]) == 0
            if is_first_index or is_parented_to_first_index:
                placement = 0
            else:
                placement = 1
    elif context.scene.skp_shape_key_new_placement == "ABOVE":
        if context.scene.skp_shape_key_auto_parent or not exists(original_parent):
            placement = original_index
        else:
            placement = SKP.get_key_index(original_parents[-1])
    elif context.scene.skp_shape_key_new_placement == "BELOW":
        if context.scene.skp_shape_key_auto_parent or not exists(original_parent):
            placement = original_index + capacity + 1
        else:
            # the capacity of original_parents[-1] won't be increased beforehand if auto-parent is turned off
            placement = SKP.get_key_index(original_parents[-1]) + SKP.get_folder_capacity(original_parents[-1]) + 1
    elif context.scene.skp_shape_key_new_placement == "BOTTOM":
        if exists(original_parent) and context.scene.skp_shape_key_auto_parent:
            placement = original_parent_index + original_parent_capacity + 1
        else:
            placement = len(shape_keys.key_blocks) - 1
    
    move_shape_key_to(origin = SKP.get_key_index(copy), destination = placement + offset)

def parent_key(key, parent, index = None, add = False, reference = None):
    if key.name != parent.name:
        key_parent = SKP.get_key_parent(key)
        if exists(key_parent):
            SKP.shift_folder_children_value(key_parent, -1)
        
        shape_keys = bpy.context.object.data.shape_keys
        key_index = SKP.get_key_index(key)
        parent_index = SKP.get_key_index(parent)
        children = SKP.get_folder_children(key)
        
        # getting the old capacity and manually adding 1 prevents
        # any nearby folder's capacity from being added to this one
        capacity = SKP.get_folder_capacity(parent) + 1
        SKP.shift_folder_children_value(parent, 1)
        
        if exists(index):
            move_shape_key_to(origin = key_index, destination = index)
        else:
            if add and exists(reference): # if auto-parent is triggered while a regular key (non-folder) is selected
                fix_new_placement(reference, key, internal = True, reference_parent_capacity = capacity)
            else:
                fix_parent_placement(key, parent, capacity = capacity)
        
        if SKP.is_key_folder(key):
            SKP.set_folder_stack_value(key, len(SKP.get_key_parents(key)) + 1)
            
            for c in children:
                if SKP.is_key_folder(c):
                    SKP.set_folder_stack_value(c, len(SKP.get_key_parents(c)) + 1)
        
        SKP.toggle_folder(parent, True)

def unparent_key(key, clear = False, move = True):
    parents = SKP.get_key_parents(key)
    children = SKP.get_folder_children(key)
    
    first_parent = parents[0]
    last_parent = parents[-1]
    
    key_index = SKP.get_key_index(key)
    key_capacity = SKP.get_folder_capacity(key)
    first_parent_index = SKP.get_key_index(first_parent)
    last_parent_index = SKP.get_key_index(last_parent)
    first_parent_capacity = SKP.get_folder_capacity(first_parent)
    last_parent_capacity = SKP.get_folder_capacity(last_parent)
    
    SKP.shift_folder_children_value(first_parent, -1)
    
    if clear and len(parents) > 1:
        # when clearing a folder's parents
        if SKP.is_key_folder(key):
            SKP.set_folder_stack_value(key, 1)
            
            if move:
                move_shape_key_to(origin = key_index, destination = last_parent_index)
            
            for i, c in enumerate(children):
                if move:
                    move_shape_key_to(origin = SKP.get_key_index(c), destination = last_parent_index + 1 + i)
                
                if SKP.is_key_folder(c):
                    SKP.set_folder_stack_value(c, len(SKP.get_key_parents(c)) + 1)
        # when clearing a single key's parents
        else:
            if move:
                move_shape_key_to(origin = key_index, destination = last_parent_index)
    else:
        # when unparenting a folder
        if SKP.is_key_folder(key):
            parent_of_parent = SKP.get_key_parent(first_parent)
            
            SKP.shift_folder_stack_value(key, -1)
            
            if exists(parent_of_parent):
                if move: # the parent of the parent only needs its capacity increased if the current key is being moved to it
                    SKP.shift_folder_children_value(parent_of_parent, 1)
            
            if move:
                move_shape_key_to(origin = key_index, destination = first_parent_index)
            
            for i, c in enumerate(children):
                if move:
                    move_shape_key_to(origin = SKP.get_key_index(c), destination = first_parent_index + 1 + i)
                
                if SKP.is_key_folder(c):
                    SKP.shift_folder_stack_value(c, -1)
        # when unparenting a single key
        else:
            parent_of_parent = SKP.get_key_parent(first_parent)
            
            if exists(parent_of_parent):
                if move:
                    SKP.shift_folder_children_value(parent_of_parent, 1)
            
            if move:
                move_shape_key_to(origin = key_index, destination = first_parent_index)
    
    if move:
        fix_unparent_placement(key)

def add_new_shape_key(type, raw = False, context = None):
    if context is None:
        context = bpy.context
    
    if type == "FROM_MIX":
        new_key = bpy.context.object.shape_key_add(from_mix = True)
    elif type == "FROM_MIX_SELECTED":
        selected = []
        
        for i, key in enumerate(context.object.data.shape_keys.key_blocks):
            if not shape_key_selected(i):
                if not key.mute:
                    key.mute = True
                    selected.append(i)
        
        new_key = bpy.context.object.shape_key_add(from_mix = True)
        
        for i in selected:
            context.object.data.shape_keys.key_blocks[i].mute = False
        
        context.scene.skp_shape_key_selections.clear()
    else:
        new_key = bpy.context.object.shape_key_add(from_mix = False)
    
    obj = context.object
    shape_keys = obj.data.shape_keys
    new_index = len(shape_keys.key_blocks) - 1
    active_key = obj.active_shape_key
    active_index = obj.active_shape_key_index
    active_parent = SKP.get_key_parent(active_key)
    
    if type == "FOLDER":
        folder_count = 1
        
        for key in shape_keys.key_blocks:
            if SKP.is_key_folder(key):
                folder_count += 1
        
        new_key.vertex_group = SKP.create_folder_data()
        new_key.name = "Folder " + str(folder_count)
    else:
        if len(shape_keys.key_blocks) == 1:
            new_key.name = "Basis"
        else:
            new_key.name = "Key " + str(len(shape_keys.key_blocks) - 1)
        
    obj.active_shape_key_index = new_index
    
    if not raw:
        if exists(active_key):
            active_parent = SKP.get_key_parent(active_key)
            is_active_folder = SKP.is_key_folder(active_key)
            is_active_parented = exists(active_parent)
            
            # prioritize the selected key as the new key's parent if the selected key is a folder
            if is_active_folder:
                parent = active_key
            # if the selected key isn't a folder, use its parent as the new key's parent
            elif is_active_parented:
                parent = active_parent
            
            if context.scene.skp_shape_key_auto_parent and (is_active_folder or is_active_parented):
                SKP.toggle_folder(parent, True) # open the folder if something is being added to it
                if is_active_parented and not is_active_folder:
                    bpy.ops.object.skp_parent(child = new_key.name, parent = parent.name, add = True, reference = active_key.name)
                else:
                    bpy.ops.object.skp_parent(child = new_key.name, parent = parent.name)
            else:
                fix_new_placement(active_key, new_key)
    
    return new_key

#################################################################################################
############################################# MENUS #############################################
#################################################################################################

class MESH_MT_skp_shape_key_add_specials(bpy.types.Menu):
    bl_label = "Shape Key Add Specials"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.skp_shape_key_add", icon = 'FILE_TEXT', text = "New Shape From Mix").type = "FROM_MIX"
        
        if len(selected_shape_keys()) > 0:
            layout.operator("object.skp_shape_key_add", icon = 'SAVE_COPY', text = "New Shape From Mix (Selected)").type = "FROM_MIX_SELECTED"
        
        layout.operator("object.skp_shape_key_add", icon = 'NEWFOLDER', text = "New Folder").type = "FOLDER"

class MESH_MT_skp_shape_key_copy_specials(bpy.types.Menu):
    bl_label = "Shape Key Copy Specials"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.skp_shape_key_copy", icon = "PASTEFLIPDOWN", text = "Copy Shape Mirrored").type = "MIRROR"
        layout.operator("object.skp_shape_key_copy", icon = "PASTEFLIPDOWN", text = "Copy Shape Mirrored (Topology)").type = "MIRROR_TOPOLOGY"

class MESH_MT_skp_shape_key_remove_specials(bpy.types.Menu):
    bl_label = "Shape Key Removal Specials"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.skp_shape_key_remove", icon = "CANCEL", text = "Delete All Shapes").type = "ALL"

class MESH_MT_skp_shape_key_other_specials(bpy.types.Menu):
    bl_label = "Other Shape Key Specials"
    
    def draw(self, context):
        layout = self.layout
        
        active_shape_key_exists = exists(context.object.active_shape_key)
        is_current_folder = SKP.is_key_folder(context.object.active_shape_key)
        
        if active_shape_key_exists:
            layout.menu("OBJECT_MT_skp_parent", icon = "FILE_PARENT")
        
        if active_shape_key_exists and is_current_folder:
            layout.menu("OBJECT_MT_skp_folder_icon", icon = "COLOR")
        else:
            layout.menu("OBJECT_MT_skp_folder_icon", icon = "COLOR", text = "Set Default Folder Icon to")
        
        layout.operator("object.shape_key_mirror", icon = "ARROW_LEFTRIGHT").use_topology = False
        layout.operator("object.shape_key_mirror", text = "Mirror Shape Key (Topology)", icon = "ARROW_LEFTRIGHT").use_topology = True
        layout.operator("object.shape_key_transfer", icon = "COPY_ID")
        layout.operator("object.join_shapes", icon = "COPY_ID")
        
        if context.user_preferences.addons[__name__].preferences.enable_debugging:
            if active_shape_key_exists:
                layout.operator("object.skp_debug_folder_data", icon = "ERROR")

class OBJECT_MT_skp_parent(bpy.types.Menu):
    bl_label = "Set Parent to"
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        shape_keys = obj.data.shape_keys
        
        if exists(obj.active_shape_key):
            has_folder = False
            active = obj.active_shape_key
            parents = SKP.get_key_parents(active)
            parent = parents[0] if len(parents) > 0 else None
            
            op = layout.operator("object.skp_parent", text = "New Folder", icon = "NEWFOLDER")
            op.type = "NEW"
            op.child = obj.active_shape_key.name
            op.parent = parent.name if exists(parent) else ""
            
            if exists(parent):
                if len(parents) > 1: # check if this shape key has stacked parents
                    op = layout.operator("object.skp_parent", text = "Clear Parents", icon = "CANCEL")
                    op.type = "CLEAR"
                    op.child = obj.active_shape_key.name
                    op.parent = parent.name
                
                op = layout.operator("object.skp_parent", text = "Remove from " + parent.name, icon = "X")
                op.type = "UNPARENT"
                op.child = obj.active_shape_key.name
                op.parent = parent.name
            
            # only allow parenting to a folder that this shape key isn't already related to
            for i, key in enumerate(shape_keys.key_blocks):
                is_folder = SKP.is_key_folder(key)
                is_current_key = key.name == active.name
                is_parent = exists(parent) and parent.name == key.name
                key_parent = SKP.get_key_parent(key)
                is_child = key in SKP.get_folder_children(active)
                
                if is_folder and not is_current_key and not is_parent and not is_child:
                    has_folder = True
                    op = layout.operator("object.skp_parent", text = ("  " * len(SKP.get_key_parents(key))) + key.name, icon = "FILE_FOLDER")
                    op.type = "PARENT"
                    op.child = obj.active_shape_key.name
                    op.parent = key.name

class OBJECT_MT_skp_folder_icon(bpy.types.Menu):
    bl_label = "Set Folder Icon to"
    
    def draw(self, context):
        layout = self.layout
        active_key = context.object.active_shape_key
        
        if exists(active_key) and SKP.is_key_folder(active_key):
            icons_block = SKP.block_value(active_key.vertex_group, SKP.icons)
            icons_swap_block = SKP.block_value(active_key.vertex_group, SKP.icons_swap) == 1
            icons_default = context.scene.skp_folder_icon_pair
            icons_default_swap = context.scene.skp_folder_icon_swap
            
            op = layout.operator("object.skp_folder_icon", icon = SKP.icon_pairs[icons_default][1 if icons_default_swap else 0], text = SKP.icon_pairs[icons_default][2] + " (Default)")
            op.icons = icons_default
            op.swap = icons_default_swap
            op.set_as_default = False
            layout.label(text = "", icon = SKP.icon_pairs[icons_default][0 if icons_default_swap else 1])
            
            op = layout.operator("object.skp_folder_icon", icon = SKP.icon_pairs[icons_block][0 if icons_swap_block else 1], text = "Swap (Active)")
            op.icons = icons_block
            op.swap = not icons_swap_block
            op.set_as_default = False
            layout.label(text = "", icon = SKP.icon_pairs[icons_block][1 if icons_swap_block else 0])
        
        for i, p in enumerate(SKP.icon_pairs):
            op = layout.operator("object.skp_folder_icon", icon = p[0], text = p[2])
            op.icons = i
            op.swap = False
            op.set_as_default = not exists(active_key) or not SKP.is_key_folder(active_key)
            layout.label(text = "", icon = p[1])

#################################################################################################
########################################## OPERATORS ############################################
#################################################################################################

class OBJECT_OT_skp_folder_icon(bpy.types.Operator):
    bl_idname = "object.skp_folder_icon"
    bl_label = "Set As Folder Icon"
    bl_options = {"REGISTER", "UNDO"}
    
    icons = bpy.props.IntProperty(options = {"HIDDEN"})
    swap = bpy.props.BoolProperty(name = "Swap", default = False)
    set_as_default = bpy.props.BoolProperty(name = "Set Default", default = False)
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key = obj.active_shape_key
        
        if exists(key) and SKP.is_key_folder(key):
            key.vertex_group = SKP.block_set(key.vertex_group, SKP.icons, self.icons)
            key.vertex_group = SKP.block_set(key.vertex_group, SKP.icons_swap, 1 if self.swap else 0)
        
        if self.set_as_default:
            bpy.context.scene.skp_folder_icon_pair = self.icons
            bpy.context.scene.skp_folder_icon_swap = 1 if self.swap else 0
        
        return {"FINISHED"}

class OBJECT_OT_skp_parent(bpy.types.Operator):
    bl_idname = "object.skp_parent"
    bl_label = "Set As Parent"
    bl_options = {"REGISTER", "UNDO"}
    
    type_options = [
        ("PARENT", "", ""),
        ("UNPARENT", "", ""),
        ("CLEAR", "", ""),
        ("NEW", "", "")
    ]
    
    type = bpy.props.EnumProperty(items = type_options, default = "PARENT", options = {"HIDDEN"})
    child = bpy.props.StringProperty(options = {"HIDDEN"})
    parent = bpy.props.StringProperty(options = {"HIDDEN"})
    add = bpy.props.BoolProperty(options = {"HIDDEN"}) # for auto-parent
    reference = bpy.props.StringProperty(options = {"HIDDEN"}) # for auto-parent
    
    @classmethod
    def poll(cls, context):
        return context.object.mode != 'EDIT'
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        
        child = shape_keys.key_blocks.get(self.child)
        parent = shape_keys.key_blocks.get(self.parent)
        reference = shape_keys.key_blocks.get(self.reference)
        
        if self.type == "PARENT":
            parent_key(child, parent, add = self.add, reference = reference)
            
        elif self.type == "UNPARENT":
            unparent_key(child)
            
        elif self.type == "CLEAR":
            unparent_key(child, clear = True)
        
        elif self.type == "NEW":
            new_folder = add_new_shape_key(type = "FOLDER", raw = True, context = context)
            if self.parent != "":
                parent_key(new_folder, parent, index = SKP.get_key_index(child))
            else:
                SKP.set_folder_stack_value(new_folder, 1)
                move_shape_key_to(origin = SKP.get_key_index(new_folder), destination = SKP.get_key_index(child))
            parent_key(child, new_folder)
        
        # force update SKP data to ensure that the UI updates
        SKP.data(True)
        
        return {"FINISHED"}

class OBJECT_OT_skp_shape_key_add(bpy.types.Operator):
    bl_idname = "object.skp_shape_key_add"
    bl_label = "Add Shape Key"
    bl_description = "Add shape key to the object"
    bl_options = {"REGISTER", "UNDO"}
    
    type_options = [
        ("NONE", "", ""),
        ("FROM_MIX", "", ""),
        ("FROM_MIX_SELECTED", "", ""),
        ("FOLDER", "", "")
    ]
    
    type = bpy.props.EnumProperty(items = type_options, default = "NONE", options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.mode != 'EDIT' and context.object.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}
    
    def execute(self, context):
        add_new_shape_key(self.type, context = context)
        return {"FINISHED"}

class OBJECT_OT_skp_shape_key_remove(bpy.types.Operator):
    bl_idname = "object.skp_shape_key_remove"
    bl_label = "Remove Shape Key"
    bl_description = "Remove shape key from the object"
    bl_options = {"REGISTER", "UNDO"}
    
    type_options = [
        ("NONE", "", ""),
        ("ALL", "", "")
    ]
    
    type = bpy.props.EnumProperty(items = type_options, default = "NONE", options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        return \
            context.object.mode != 'EDIT' and \
            exists(context.object.active_shape_key)
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        selection = obj.active_shape_key_index
        active = obj.active_shape_key
        
        context.scene.skp_shape_key_selections.clear()
        
        parent = SKP.get_key_parent(active)
        previous_key = shape_keys.key_blocks[selection - 1] if selection - 1 >= 0 else None
        next_key = shape_keys.key_blocks[selection + 1] if selection + 1 < len(shape_keys.key_blocks) else None
        previous_key_parent = SKP.get_key_parent(previous_key) if exists(previous_key) else None
        next_key_parent = SKP.get_key_parent(next_key) if exists(next_key) else None
        
        siblings = SKP.get_key_siblings(active) # store selection data
        
        def delete_key():
            is_folder = SKP.is_key_folder(active)
            children = SKP.get_folder_children(active)
            capacity = len(children)
            
            if is_folder:
                obj.active_shape_key_index = SKP.get_key_index(active)
                bpy.ops.object.shape_key_remove()
                
                if exists(parent):
                    SKP.shift_folder_children_value(parent, -1)
                
                for c in children:
                    obj.active_shape_key_index = SKP.get_key_index(c)
                    bpy.ops.object.shape_key_remove()
            else:
                obj.active_shape_key_index = SKP.get_key_index(active)
                bpy.ops.object.shape_key_remove()
                
                if exists(parent):
                    SKP.shift_folder_children_value(parent, -1)
        
        if self.type == "ALL":
            bpy.ops.object.shape_key_remove(all = True)
        elif self.type == "NONE":
            delete_key()
            
            # fix selection
            if exists(siblings[0]) and siblings[0].name != shape_keys.reference_key.name:
                obj.active_shape_key_index = SKP.get_key_index(siblings[0])
            elif exists(siblings[1]):
                obj.active_shape_key_index = SKP.get_key_index(siblings[1])
        
        return {"FINISHED"}

class OBJECT_OT_skp_shape_key_copy(bpy.types.Operator):
    bl_label = "Copy Shape"
    bl_idname = "object.skp_shape_key_copy"
    bl_description = "Copy the active shape key"
    bl_options = {"REGISTER", "UNDO"}
    
    type_options = [
        ("NONE", "", ""),
        ("MIRROR", "", ""),
        ("MIRROR_TOPOLOGY", "", "")
    ]
    
    type = bpy.props.EnumProperty(items = type_options, default = "NONE", options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        return \
            context.object.mode != 'EDIT' and \
            exists(context.object.active_shape_key)
    
    def execute(self, context):
        obj = context.object
        active_key = obj.active_shape_key
        active_key_index = obj.active_shape_key_index
        shape_keys = obj.data.shape_keys
        basis = shape_keys.reference_key
        
        # create a new temporary key to find default values
        default_key = context.object.shape_key_add(from_mix = False)
        default_interpolation = default_key.interpolation
        context.object.shape_key_remove(default_key)
        
        obj.active_shape_key_index = active_key_index
        
        def copy(key, raw = False):
            unmuted_keys = []
            
            for kb in shape_keys.key_blocks:
                if kb.mute == False and kb.name != key.name and kb.name != basis.name:
                    unmuted_keys.append(kb)
                    kb.mute = True
            
            # store original values
            old_name = key.name
            old_slider_min = key.slider_min
            old_slider_max = key.slider_max
            old_value = key.value
            old_vertex_group = key.vertex_group
            old_relative_key = key.relative_key
            old_interpolation = key.interpolation
            old_mute = key.mute
            
            # prepare shape key for full copy
            key.slider_min = 0.0
            key.slider_max = 1.0
            key.value = 1.0
            key.vertex_group = ""
            key.relative_key = basis
            key.interpolation = default_interpolation
            key.mute = False
            
            if raw:
                new_key = context.object.shape_key_add(from_mix = True)
            else:
                new_key = add_new_shape_key(type = "FROM_MIX", context = context)
            
            obj.active_shape_key_index = SKP.get_key_index(new_key)
            
            if self.type == "MIRROR" or self.type == "MIRROR_TOPOLOGY":
                bpy.ops.object.shape_key_mirror(use_topology = self.type == "MIRROR_TOPOLOGY")
                
                if old_name.endswith(".L"):
                    old_name = old_name[:-2] + ".R"
                elif old_name.endswith(".R"):
                    old_name = old_name[:-2] + ".L"
            
            # copy original values
            new_key.name = old_name
            new_key.slider_min = old_slider_min
            new_key.slider_max = old_slider_max
            new_key.value = old_value
            new_key.vertex_group = old_vertex_group
            new_key.relative_key = old_relative_key
            new_key.interpolation = old_interpolation
            new_key.mute = old_mute
            
            # restore original values
            key.slider_min = old_slider_min
            key.slider_max = old_slider_max
            key.value = old_value
            key.vertex_group = old_vertex_group
            key.relative_key = old_relative_key
            key.interpolation = old_interpolation
            key.mute = old_mute
            
            for key in unmuted_keys:
                key.mute = False
            
            return new_key
        
        if SKP.is_key_folder(active_key):
            children = SKP.get_folder_children(active_key)
            parent = copy(active_key, raw = True)
            
            parent_index = SKP.get_key_index(parent)
            
            for i, c in enumerate(children):
                child = copy(c, raw = True)
            
            active_parent = SKP.get_key_parent(active_key)
            
            if exists(active_parent):
                active_parent_capacity = SKP.get_folder_capacity(active_parent)
                
                if context.scene.skp_shape_key_auto_parent:
                    SKP.shift_folder_children_value(active_parent, 1)
                else:
                    SKP.set_folder_stack_value(parent, 1)
                    
                    for c in SKP.get_folder_children(parent):
                        SKP.set_folder_stack_value(c, len(SKP.get_key_parents(c)) + 1)
                
                fix_copy_placement(active_key, parent, original_parent_capacity = active_parent_capacity)
                
                obj.active_shape_key_index = SKP.get_key_index(parent)
            else:
                fix_copy_placement(active_key, parent)
                
                obj.active_shape_key_index = SKP.get_key_index(parent)
        else:
            copy(active_key)
        
        return {'FINISHED'}

class OBJECT_OT_skp_shape_key_move(bpy.types.Operator):
    bl_idname = "object.skp_shape_key_move"
    bl_label = "Move Shape Key"
    bl_description = "Move the active shape key up/down in the list"
    bl_options = {"REGISTER", "UNDO"}
    
    type_options = [
        ("TOP", "Top", ""),
        ("UP", "Up", ""),
        ("DOWN", "Down", ""),
        ("BOTTOM", "Bottom", "")
    ]
    
    type = bpy.props.EnumProperty(name = "Type", items = type_options)
    origin = bpy.props.IntProperty(default = -1, options = {"HIDDEN"})
    destination = bpy.props.IntProperty(name = "Destination", options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        # check if multiple shape keys exist before attempting to move
        # check if the first shape key is a folder with children
        return \
            context.object and \
            context.object.mode != 'EDIT' and \
            exists(context.object.active_shape_key) and \
            len(context.object.data.shape_keys.key_blocks) > 1 and \
            (SKP.get_folder_capacity(context.object.data.shape_keys.key_blocks[0]) + 1 < len(context.object.data.shape_keys.key_blocks) or \
            context.object.active_shape_key_index > 0)
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        data = skp_data(context)
        
        context.scene.skp_shape_key_selections.clear()
        
        def move_folder_direction(name, capacity, type):
            index = shape_keys.key_blocks.find(name)
            r = range(index, index + capacity + 1) if type == "UP" else reversed(range(index, index + capacity + 1))
            
            for i in r:
                obj.active_shape_key_index = i
                bpy.ops.object.shape_key_move(type = type)
                
            obj.active_shape_key_index = index - 1 if type == "UP" else index + 1
        
        # move once in one direction, respecting hierarchy
        def move_direction(index, type):
            obj.active_shape_key_index = index
            current = data[index]
            next_key = data[index].previous_key if type == "UP" else data[index].next_key
            
            next = metadata(data, next_key) if exists(next_key) else None
            parent = metadata(data, current.parents[0]) if current.is_parented else None
            next_parent = metadata(data, next.parents[0]) if exists(next) and next.is_parented else None
            
            def is_type_up():
                return type == "UP"
            def is_type_down():
                return type == "DOWN"
            def is_type_top():
                return type == "TOP"
            def is_type_bottom():
                return type == "BOTTOM"
            def is_current_folder():
                return current.is_folder
            def is_next_folder():
                return next.is_folder if exists(next) else False
            def is_current_only_child():
                if exists(parent):
                    is_only_child = SKP.get_folder_children_value(parent.key) == 1
                else:
                    is_only_child = len(shape_keys.key_blocks) == 1
                
                return is_only_child
            def is_current_first_child():
                if exists(parent):
                    is_first_child = current.key.name == parent.first_child.name
                else:
                    is_first_child = current.key.name == shape_keys.key_blocks[0].name
                
                return is_first_child
            def is_current_last_child():
                if current.has_children:
                    if exists(parent):
                        is_last_child = current.last_child.name == parent.last_child.name
                    else:
                        is_last_child = current.last_child.name == shape_keys.key_blocks[-1].name
                else:
                    is_last_child = current.is_last_child
                
                return is_last_child
            
            def is_next_last_child():
                return next.is_last_child if exists(next) else False
            
            def move_default():
                if is_current_folder():
                    move_folder_direction(current.key.name, current.capacity, type)
                else:
                    bpy.ops.object.shape_key_move(type = type)
            def move_to_bottom(folder):
                if exists(folder):
                    if is_current_folder():
                        for _ in range(index, folder.last_child_index - current.capacity):
                            move_folder_direction(current.key.name, current.capacity, "DOWN")
                    else:
                        for _ in range(index, folder.last_child_index):
                            bpy.ops.object.shape_key_move(type = "DOWN")
                else:
                    if is_current_folder():
                        for _ in range(index, len(shape_keys.key_blocks) - 1 - current.capacity):
                            move_folder_direction(current.key.name, current.capacity, "DOWN")
                    else:
                        for _ in range(index, len(shape_keys.key_blocks) - 1):
                            bpy.ops.object.shape_key_move(type = "DOWN")
            def move_to_top(folder):
                if exists(folder):
                    if is_current_folder():
                        for _ in range(folder.first_child_index, index):
                            move_folder_direction(current.key.name, current.capacity, "UP")
                    else:
                        for _ in range(folder.first_child_index, index):
                            bpy.ops.object.shape_key_move(type = "UP")
                else:
                    if SKP.is_key_folder(shape_keys.key_blocks[0]):
                        fi = SKP.get_folder_capacity(shape_keys.key_blocks[0]) + 1
                        r = fi if index > fi else 0
                    else:
                        r = 1 if index > 1 else 0
                    
                    if is_current_folder():
                        for _ in range(r, index):
                            move_folder_direction(current.key.name, current.capacity, "UP")
                    else:
                        for _ in range(r, index):
                            bpy.ops.object.shape_key_move(type = "UP")
            def skip_over_folder(folder):
                current_stack = current.stack + 1
                folder_stack = folder.stack
                
                if current_stack < folder_stack + 1:
                    folder = metadata(data, folder.parents[folder_stack - current_stack])
                
                if is_current_folder():
                    for _ in range(folder.capacity + 1):
                        move_folder_direction(current.key.name, current.capacity, type)
                else:
                    for _ in range(folder.capacity + 1):
                        bpy.ops.object.shape_key_move(type = type)
            
            if is_current_only_child():
                pass
            elif is_type_top():
                move_to_top(parent)
            elif is_type_bottom():
                move_to_bottom(parent)
            elif is_current_first_child():
                if is_type_up():
                    move_to_bottom(parent)
                elif is_type_down():
                    if is_next_folder():
                        skip_over_folder(next)
                    else:
                        move_default()
            elif is_current_last_child():
                if is_type_up():
                    if is_next_last_child():
                        skip_over_folder(next_parent)
                    else:
                        move_default()
                elif is_type_down():
                    move_to_top(parent)
            else:
                if is_type_up():
                    if is_next_last_child():
                        skip_over_folder(next_parent)
                    else:
                        move_default()
                elif is_type_down():
                    if is_next_folder():
                        skip_over_folder(next)
                    else:
                        move_default()
        
        origin = self.origin if self.origin != -1 else obj.active_shape_key_index
        destination = self.destination
        
        if self.type == "TOP":
            destination = 1 if origin > 1 else 0
        elif self.type == "UP":
            destination = origin - 1
        elif self.type == "DOWN":
            destination = origin + 1
        elif self.type == "BOTTOM":
            destination = len(shape_keys.key_blocks) - 1
        
        move_direction(origin, self.type)
        
        return {"FINISHED"}


class OBJECT_OT_skp_shape_key_select(bpy.types.Operator):
    bl_label = "Select/Deselect Shape Key"
    bl_idname = "object.skp_shape_key_select"
    bl_options = {"REGISTER", "UNDO"}
    
    mode_options = [
        ("TOGGLE", "", ""),
        ("ALL", "", ""),
        ("NONE", "", ""),
        ("INVERSE", "", "")
    ]
    
    mode = bpy.props.EnumProperty(items = mode_options, options = {"HIDDEN"})
    index = bpy.props.IntProperty(default = -1, options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        def valid_selection(i):
            return i > 0 and not SKP.is_key_folder(shape_keys.key_blocks[i])
        
        if self.mode == "TOGGLE":
            if valid_selection(self.index):
                if self.index in context.scene.skp_shape_key_selections:
                    context.scene.skp_shape_key_selections[self.index] = not context.scene.skp_shape_key_selections[self.index]
                else:
                    context.scene.skp_shape_key_selections[self.index] = True
        elif self.mode == "ALL":
            for i, key in enumerate(shape_keys.key_blocks):
                if valid_selection(i):
                    context.scene.skp_shape_key_selections[i] = True
        elif self.mode == "NONE":
            for i, key in enumerate(shape_keys.key_blocks):
                if valid_selection(i):
                    context.scene.skp_shape_key_selections[i] = False
        elif self.mode == "INVERSE":
            for i, key in enumerate(shape_keys.key_blocks):
                if valid_selection(i):
                    if i in context.scene.skp_shape_key_selections:
                        context.scene.skp_shape_key_selections[i] = not context.scene.skp_shape_key_selections[i]
                    else:
                        context.scene.skp_shape_key_selections[i] = True
        
        return {"FINISHED"}

class OBJECT_OT_skp_folder_toggle(bpy.types.Operator):
    bl_label = "Expand/Collapse"
    bl_idname = "object.skp_folder_toggle"
    bl_description = "Show or hide this folder's children"
    bl_options = {"REGISTER", "UNDO"}
    
    index = bpy.props.IntProperty(options = {"HIDDEN"})
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        active_parents = SKP.get_key_parents(active_key) if exists(active_key) else None
        folder = shape_keys.key_blocks[self.index]
        
        if len(active_parents) > 0 and folder in active_parents:
            obj.active_shape_key_index = self.index
        
        SKP.toggle_folder(folder)
        
        return {"FINISHED"}

class OBJECT_OT_skp_folder_ungroup(bpy.types.Operator):
    bl_label = "Ungroup Folder"
    bl_idname = "object.skp_folder_ungroup"
    bl_description = "Ungroup this folder"
    bl_options = {"REGISTER", "UNDO"}
    
    index = bpy.props.IntProperty(options = {"HIDDEN"})
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        key = shape_keys.key_blocks[self.index]
        is_folder = SKP.is_key_folder(key)
        children = SKP.get_folder_children(key)
        parent = SKP.get_key_parent(key)
        
        SKP.toggle_folder(key, expand = True)
        
        old_selection = obj.active_shape_key_index
        
        if exists(parent):
            SKP.shift_folder_children_value(parent, SKP.get_folder_children_value(key) - 1)
        
        for c in children:
            if SKP.is_key_folder(c):
                SKP.shift_folder_stack_value(c, -1)
        
        obj.active_shape_key_index = self.index
        bpy.ops.object.shape_key_remove()
        
        # fix selection
        obj.active_shape_key_index = old_selection - (1 if (old_selection > self.index or len(children) == 0) else 0)
        
        return {"FINISHED"}

class DRIVER_OT_skp_driver_update(bpy.types.Operator):
    bl_label = "Update Driver"
    bl_idname = "driver.skp_driver_update"
    bl_description = "Force update this driver"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if exists(shape_keys) and exists(active_key):
            SKP.update_driver(SKP.get_key_driver(shape_keys, active_key))
        
        return {"FINISHED"}

class DRIVER_OT_skp_variable_add(bpy.types.Operator):
    bl_label = "Add Variable"
    bl_idname = "driver.skp_variable_add"
    bl_description = "Add a new variable for this driver"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if exists(shape_keys) and exists(active_key):
            driver = SKP.get_key_driver(shape_keys, active_key)
            
            if exists(driver):
                driver.variables.new()
        
        return {"FINISHED"}

class DRIVER_OT_skp_variable_remove(bpy.types.Operator):
    bl_label = "Remove Variable"
    bl_idname = "driver.skp_variable_remove"
    bl_description = "Remove variable from the driver"
    bl_options = {"REGISTER", "UNDO"}
    
    index = bpy.props.IntProperty(options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if exists(shape_keys) and exists(active_key):
            driver = SKP.get_key_driver(shape_keys, active_key)
            
            if exists(driver) and len(driver.variables) > self.index:
                driver.variables.remove(driver.variables[self.index])
        
        return {"FINISHED"}

class DRIVER_OT_skp_variable_copy(bpy.types.Operator):
    bl_label = "Copy Variable"
    bl_idname = "driver.skp_variable_copy"
    bl_description = "Copy this variable"
    bl_options = {"REGISTER", "UNDO"}
    
    index = bpy.props.IntProperty(options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if exists(shape_keys) and exists(active_key):
            driver = SKP.get_key_driver(shape_keys, active_key)
            
            if exists(driver) and len(driver.variables) > self.index:
                var = driver.variables.new()
                vars = list(driver.variables)
                
                vars.insert(self.index + 1, vars.pop(len(vars) - 1))
                
                var.name = vars[self.index].name + "_copy"
                var.type = vars[self.index].type
                
                for t in range(len(vars[self.index].targets)):
                    var.targets[t].bone_target = vars[self.index].targets[t].bone_target
                    var.targets[t].data_path = vars[self.index].targets[t].data_path
                    
                    if var.type == "SINGLE_PROP":
                        var.targets[t].id_type = vars[self.index].targets[t].id_type
                    
                    var.targets[t].id = vars[self.index].targets[t].id
                    var.targets[t].transform_space = vars[self.index].targets[t].transform_space
                    var.targets[t].transform_type = vars[self.index].targets[t].transform_type
                
                SKP.refresh_driver_variables(driver, vars)
        
        return {"FINISHED"}

class DRIVER_OT_skp_variable_move(bpy.types.Operator):
    bl_label = "Move Variable"
    bl_idname = "driver.skp_variable_move"
    bl_description = "Move this variable up/down in the list"
    bl_options = {"REGISTER", "UNDO"}
    
    type_options = [
        ("TOP", "", ""),
        ("UP", "", ""),
        ("DOWN", "", ""),
        ("BOTTOM", "", "")
    ]
    
    index = bpy.props.IntProperty(options = {"HIDDEN"})
    type = bpy.props.EnumProperty(items = type_options, options = {"HIDDEN"})
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys
        active_key = obj.active_shape_key
        
        if exists(shape_keys) and exists(active_key):
            driver = SKP.get_key_driver(shape_keys, active_key)
            
            if exists(driver) and len(driver.variables) > self.index:
                vars = list(driver.variables)
                
                if self.type == "TOP":
                    vars.insert(0, vars.pop(self.index))
                elif self.type == "UP" and self.index > 0:
                    vars.insert(self.index - 1, vars.pop(self.index))
                elif self.type == "DOWN" and self.index < len(vars) - 1:
                    vars.insert(self.index + 1, vars.pop(self.index))
                elif self.type == "BOTTOM":
                    vars.insert(len(vars) - 1, vars.pop(self.index))
                
                SKP.refresh_driver_variables(driver, vars)
        
        return {"FINISHED"}

class OBJECT_OT_skp_debug_folder_data(bpy.types.Operator):
    bl_label = "[ DEBUG ] Folder Data"
    bl_idname = "object.skp_debug_folder_data"
    bl_description = "Manually create folder data"
    bl_options = {"REGISTER", "UNDO"}
    
    folder = bpy.props.IntProperty(name = "Folder Iterations", default = 1, description = "Number of times to indent the folder's children (1 + [number of folder's parents])")
    children = bpy.props.IntProperty(name = "Children", default = 0, description = "The amount of children the folder has, not including children of children")
    expand = bpy.props.BoolProperty(name = "Expand", default = True, description = "Expand or collapse the folder")
    icons = bpy.props.IntProperty(name = "Icon Pair", default = 0, min = 0, max = 60, description = "The pair of icons used when the folder is expanded or collapsed")
    icons_swap = bpy.props.BoolProperty(name = "Swap Icons", default = False, description = "Swap the icons used for when the folder is expanded or collapsed")
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_shape_key
    
    def execute(self, context):
        key = context.object.active_shape_key
        
        key.vertex_group = SKP.create_folder_data(
            folder = self.folder,
            children = self.children,
            expand = 1 if self.expand else 0,
            icons = self.icons,
            icons_swap = 1 if self.icons_swap else 0)
        
        return {"FINISHED"}

#################################################################################################
############################################ MAIN UI ############################################
#################################################################################################

class OBJECT_PT_skp_shape_keys_plus(bpy.types.Panel):
    bl_label = "Shape Keys+"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'})
    
    def draw(self, context):
        layout = self.layout
        
        ob = context.object
        key = ob.data.shape_keys
        kb = ob.active_shape_key
        kb_index = ob.active_shape_key_index
        
        enable_edit = ob.mode != 'EDIT'
        enable_edit_value = False
        
        if ob.show_only_shape_key is False:
            if enable_edit or (ob.type == 'MESH' and ob.use_shape_key_edit_mode):
                enable_edit_value = True
        
        sub = layout.row()
        sub.prop(context.scene, "skp_shape_key_new_placement", text = "New")
        sub.prop(context.scene, "skp_shape_key_auto_parent")
        sub = layout.row()
        sub.prop(context.scene, "skp_shape_key_parent_placement", text = "Parent")
        sub.prop(context.scene, "skp_shape_key_unparent_placement", text = "Unparent")
        layout.prop(context.scene, "skp_shape_key_indent_scale")
        
        row = layout.row(align = True)
        row.operator("object.skp_shape_key_select", text = "All", icon = "ZOOMIN").mode = "ALL"
        row.operator("object.skp_shape_key_select", text = "None", icon = "ZOOMOUT").mode = "NONE"
        row.operator("object.skp_shape_key_select", text = "Inverse", icon = "ARROW_LEFTRIGHT").mode = "INVERSE"
        
        ROW_list = layout.row()
        
        rows = 4
        
        if exists(kb):
            rows = 8
        
        ROW_list.template_list("MESH_UL_skp_shape_keys_plus", "", key, "key_blocks", ob, "active_shape_key_index", rows = rows)
        
        col = ROW_list.column()
        
        ROW_newshape = col.row(align = True)
        ROW_copyshape = col.row(align = True)
        ROW_removeshape = col.row(align = True)
        ROW_specials = col.row(align = False)
        
        ROW_specials.scale_x = 2.0
        
        ROW_newshape.operator("object.skp_shape_key_add", icon = 'ZOOMIN', text = "").type = "NONE"
        ROW_newshape.menu("MESH_MT_skp_shape_key_add_specials", icon = 'DOWNARROW_HLT', text = "")
        
        ROW_copyshape.operator("object.skp_shape_key_copy", icon = 'PASTEDOWN', text = "").type = "NONE"
        ROW_copyshape.menu("MESH_MT_skp_shape_key_copy_specials", icon = 'DOWNARROW_HLT', text = "")
        
        ROW_removeshape.operator("object.skp_shape_key_remove", icon = 'ZOOMOUT', text = "").type = "NONE"
        ROW_removeshape.menu("MESH_MT_skp_shape_key_remove_specials", icon = 'DOWNARROW_HLT', text = "")
        
        ROW_specials.menu("MESH_MT_skp_shape_key_other_specials", icon = 'DOWNARROW_HLT', text = "")
        
        if kb:
            col.separator()
            
            sub = col.column(align = True)
            sub.operator("object.skp_shape_key_move", icon = 'TRIA_UP_BAR', text = "").type = "TOP"
            sub.operator("object.skp_shape_key_move", icon = 'TRIA_UP', text = "").type = "UP"
            sub.operator("object.skp_shape_key_move", icon = 'TRIA_DOWN', text = "").type = "DOWN"
            sub.operator("object.skp_shape_key_move", icon = 'TRIA_DOWN_BAR', text = "").type = "BOTTOM"

            split = layout.split(percentage = 0.4)
            row = split.row()
            row.enabled = enable_edit
            row.prop(key, "use_relative")
            
            row = split.row()
            row.alignment = 'RIGHT'
            
            sub = row.row(align = True)
            sub.label()
            subsub = sub.row(align = True)
            subsub.active = enable_edit_value
            subsub.prop(ob, "show_only_shape_key", text = "")
            sub.prop(ob, "use_shape_key_edit_mode", text = "")

            sub = row.row()
            
            if key.use_relative:
                sub.operator("object.shape_key_clear", icon = 'X', text = "")
            else:
                sub.operator("object.shape_key_retime", icon = 'RECOVER_LAST', text = "")
            
            if not SKP.is_key_folder(kb):
                if key.use_relative:
                    if ob.active_shape_key_index != 0:
                        row = layout.row()
                        row.active = enable_edit_value
                        row.prop(kb, "value")
                        
                        split = layout.split()
                        
                        col = split.column(align = True)
                        col.active = enable_edit_value
                        col.label(text = "Range:")
                        col.prop(kb, "slider_min", text = "Min")
                        col.prop(kb, "slider_max", text = "Max")

                        col = split.column(align = True)
                        col.active = enable_edit_value
                        col.label(text = "Blend:")
                        col.prop_search(kb, "vertex_group", ob, "vertex_groups", text = "")
                        col.prop_search(kb, "relative_key", key, "key_blocks", text = "")
                
                else:
                    layout.prop(kb, "interpolation")
                    row = layout.column()
                    row.active = enable_edit_value
                    row.prop(key, "eval_time")
            
            driver = SKP.get_key_driver(key, kb)
            
            if exists(driver):
                layout.separator()
                row = layout.row()
                row.prop(context.scene, "skp_driver_visible")
                
                if context.scene.skp_driver_visible:
                    row = layout.row()
                    row.label(text = "Type:")
                    row = row.row()
                    row.prop(driver, "type", text = "")
                    row.scale_x = 2
                    
                    if driver.type == "SCRIPTED":
                        row.prop(driver, "use_self")
                    
                    if driver.type == "SCRIPTED":
                        row = layout.row()
                        row.label(text = "Expression:")
                        row = row.row()
                        row.prop(driver, "expression", text = "")
                        row.scale_x = 4
                    
                    row = layout.row(align = True)
                    row.operator("driver.skp_variable_add", icon = "ZOOMIN")
                    row.operator("driver.skp_driver_update", icon = "FILE_REFRESH")
                    
                    for i, v in enumerate(driver.variables):
                        area_parent = layout.row()
                        area = area_parent.column(align = True)
                        box = area.box()
                        box2 = area_parent.box()
                        row = box.row()
                        row.operator("driver.skp_variable_remove", icon = "X", text = "", emboss = False).index = i
                        row.prop(driver.variables[i], "name", text = "")
                        row = row.row()
                        row.prop(driver.variables[i], "type", text = "")
                        row.scale_x = 2
                        row2 = box2.column(align = False)
                        op_copy = row2.operator("driver.skp_variable_copy", text = "", icon = "PASTEDOWN")
                        op_copy.index = i
                        row3 = box2.column(align = True)
                        op_move_top = row3.operator("driver.skp_variable_move", text = "", icon = "TRIA_UP_BAR")
                        op_move_top.index = i
                        op_move_top.type = "TOP"
                        op_move_up = row3.operator("driver.skp_variable_move", text = "", icon = "TRIA_UP")
                        op_move_up.index = i
                        op_move_up.type = "UP"
                        op_move_down = row3.operator("driver.skp_variable_move", text = "", icon = "TRIA_DOWN")
                        op_move_down.index = i
                        op_move_down.type = "DOWN"
                        op_move_bottom = row3.operator("driver.skp_variable_move", text = "", icon = "TRIA_DOWN_BAR")
                        op_move_bottom.index = i
                        op_move_bottom.type = "BOTTOM"
                        
                        if driver.variables[i].type == "SINGLE_PROP":
                            row = box.row(align = True)
                            row.prop(driver.variables[i].targets[0], "id_type", icon_only = True)
                            row = row.row(align = True)
                            row.scale_x = 8
                            row.prop(driver.variables[i].targets[0], "id", text = "")
                            
                            if exists(driver.variables[i].targets[0].id):
                                row = box.row()
                                row.prop(driver.variables[i].targets[0], "data_path", text = "", icon = "RNA")
                        elif driver.variables[i].type == "TRANSFORMS":
                            target = driver.variables[i].targets[0]
                            row = box.row(align = True)
                            row.prop(target, "id_type", icon_only = True)
                            row = row.row(align = True)
                            row.scale_x = 8
                            row.prop(target, "id", text = "", expand = True)
                            
                            if exists(target) and exists(target.id) and target.id.type == "ARMATURE":
                                row = box.column(align = True)
                                row.prop_search(target, "bone_target", target.id.data, "bones", text = "", icon = "BONE_DATA")
                            
                            row = box.row()
                            col = row.column(align = True)
                            col.prop(driver.variables[i].targets[0], "transform_type", text = "Type")
                            col.prop(driver.variables[i].targets[0], "transform_space", text = "Space")
                        elif driver.variables[i].type == "ROTATION_DIFF":
                            for i, target in enumerate(driver.variables[i].targets):
                                row = box.row()
                                row.label(text = "Bone " + str(i + 1) + ":")
                                row = row.row(align = True)
                                row.prop(target, "id_type", icon_only = True)
                                row.scale_x = 0.25
                                row = row.row(align = True)
                                row.scale_x = 8
                                row.prop(target, "id", text = "", expand = True)
                                
                                if exists(target.id) and target.id.type == "ARMATURE":
                                    row = box.column(align = True)
                                    row.prop_search(target, "bone_target", target.id.data, "bones", text = "", icon = "BONE_DATA")
                                
                                row = box.row()
                                col = row.column(align = True)
                                col.prop(target, "transform_type", text = "Type")
                                col.prop(target, "transform_space", text = "Space")
                        elif driver.variables[i].type == "LOC_DIFF":
                            for i, target in enumerate(driver.variables[i].targets):
                                row = box.row()
                                row.label(text = "Ob/Bone " + str(i + 1) + ":")
                                row = row.row(align = True)
                                row.prop(target, "id_type", icon_only = True)
                                row.scale_x = 0.25
                                row = row.row(align = True)
                                row.scale_x = 8
                                row.prop(target, "id", text = "", expand = True)
                                
                                if exists(target.id) and target.id.type == "ARMATURE":
                                    row = box.column(align = True)
                                    row.prop_search(target, "bone_target", target.id.data, "bones", text = "", icon = "BONE_DATA")
                                
                                row = box.row()
                                col = row.column(align = True)
                                col.prop(target, "transform_space")
                    

class MESH_UL_skp_shape_keys_plus(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = active_data
        shape_keys = obj.data.shape_keys
        key_block = item
        
        l1 = layout.row(align = True)
        l1.scale_x = 0.5
        parents = SKP.data()["parents"][index]
        parent = parents[0] if len(parents) > 0 else None
        is_folder = SKP.is_key_folder(key_block)
        is_selected = shape_key_selected(index)
        
        selection_exists = len(selected_shape_keys()) > 0
        
        # check if this shape key belongs in a folder
        if exists(parent):
            for _ in range(SKP.get_folder_stack_value(parent)): # get the number of folders this shape key is stacked in
                for _ in range(context.scene.skp_shape_key_indent_scale): # use the customizable folder indentation
                    l1.box()
        
        if is_folder:
            icon_pair = SKP.icon_pairs[SKP.block_value(key_block.vertex_group, SKP.icons)]
            icon_swap = SKP.block_value(key_block.vertex_group, SKP.icons_swap) == 1
            
            if SKP.block_value(key_block.vertex_group, SKP.expand) > 0:
                icon = icon_pair[1 if icon_swap else 0]
            else:
                icon = icon_pair[0 if icon_swap else 1]
            
            l1.operator("object.skp_folder_toggle", text = "", icon = icon, emboss = False).index = index
            l2 = l1.row()
            l2.scale_x = 5
            l2.prop(key_block, "name", text = "", emboss = False)
        else:
            l2 = l1.row()
            l2.scale_x = 5
            l2.prop(key_block, "name", text = "", emboss = False, icon = "FILE_TICK" if is_selected else "SHAPEKEY_DATA")
        
        row = layout.row(align = True)
        
        if is_folder:
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                row.active = False
            
            row.operator("object.skp_folder_ungroup", text = "", icon = "X", emboss = False).index = index
        else:
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                row.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text = "", emboss = False)
            elif index > 0:
                if selection_exists:
                    can_edit = is_selected
                else:
                    can_edit = True
                
                if can_edit:
                    row.prop(key_block, "value", text = "", emboss = False)
                else:
                    row.label(str(key_block.value))
            else:
                row.label(text = "")
            
            row.prop(key_block, "mute", text = "", emboss = False)
            
            if index > 0 and not is_folder:
                op = row.operator("object.skp_shape_key_select", text = "", icon = "CHECKBOX_HLT" if is_selected else "CHECKBOX_DEHLT", emboss = False)
                op.index = index
                op.mode = "TOGGLE"
    
    def draw_filter(self, context, layout):
        row = layout.row()

        subrow = row.row(align = True)
        subrow.prop(self, "filter_name", text = "")
        icon = "ZOOM_OUT" if self.use_filter_invert else "ZOOM_IN"
        subrow.prop(self, "use_filter_invert", text = "", icon = icon)
        icon = "FILE_FOLDER"
        subrow.prop(context.scene, "skp_show_filtered_folder_contents", text = "", icon = icon)
        subrow = row.row(align = True)
        icon = "RESTRICT_VIEW_OFF"
        subrow.prop(context.scene, "skp_shape_key_limit_to_active", text = "", icon = icon)
        
        if context.scene.skp_shape_key_limit_to_active:
            subrow.prop(context.scene, "skp_filter_active_threshold", text = "")
            icon = "TRIA_LEFT" if context.scene.skp_filter_active_below else "TRIA_RIGHT"
            subrow.prop(context.scene, "skp_filter_active_below", text = "", icon = icon)
    
    def filter_items(self, context, data, propname):
        flt_flags = []
        flt_name_flags = []
        flt_neworder = []
        
        shape_keys = context.object.data.shape_keys
        key_blocks = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        filtering_by_name = False
        name_filters = [False] * len(key_blocks)
        
        def filter_set(i, f):
            # self.bitflag_filter_item will allow a shape key to be shown
            # 0 will prevent a shape key from being shown
            flt_flags[i] = self.bitflag_filter_item if f else 0
        
        def filter_get(i):
            return flt_flags[i] is not 0
        
        if self.filter_name:
            filtering_by_name = True
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, key_blocks, "name")
            
            for i in range(len(flt_flags)):
                if flt_flags[i] == self.bitflag_filter_item:
                    name_filters[i] = True
        else:
            # initialize every shape key as visible
            flt_flags = [self.bitflag_filter_item] * len(key_blocks)
        
        for idx, key in enumerate(key_blocks):
            skp_data = SKP.data()
            parents = skp_data["parents"][idx]
            
            hidden = False
            
            if len(parents) > 0:
                parent_collapsed = False
                
                for p in parents:
                    if SKP.block_value(p.vertex_group, SKP.expand) == 0:
                        parent_collapsed = True
                        break
                
                if parent_collapsed and not filtering_by_name:
                    hidden = True
            
            if hidden:
                filter_set(idx, False)
            
            if filtering_by_name:
                if len(parents) > 0:
                    for p in parents:
                        parent_index = SKP.get_key_index(p)
                        parent_hidden = not name_filters[parent_index]
                        
                        if name_filters[idx] and parent_hidden:
                            filter_set(parent_index, True)
            
            if context.scene.skp_show_filtered_folder_contents and SKP.is_key_folder(key) and filter_get(idx):
                children = skp_data["children"][idx]
                
                if len(children) > 0:
                    for i in range(len(children)):
                        filter_set(idx + 1 + i, True)
            
            if context.scene.skp_shape_key_limit_to_active:
                if SKP.is_key_folder(key):
                    filter_set(idx, False)
                else:
                    val = context.scene.skp_filter_active_threshold
                    below = context.scene.skp_filter_active_below
                    filter_set(idx, (key.value >= val) if not below else (key.value <= val))
        
        return flt_flags, flt_neworder

#################################################################################################
######################################## REGISTRATION ###########################################
#################################################################################################

def extensions():
    shape_key_new_placement_options = [
        ("BOTTOM", "Bottom", "Place all new shape keys at the bottom of the list"),
        ("BELOW", "Below", "Place all new shape keys under the active key"),
        ("ABOVE", "Above", "Place all new shape keys below the active key"),
        ("TOP", "Top", "Place all new shape keys at the top of the list")
    ]
    
    shape_key_parent_placement_options = [
        ("BOTTOM", "Bottom", "Place newly parented shape keys at the bottom of the list"),
        ("TOP", "Top", "Place newly parented shape keys at the top of the list")
    ]
    
    shape_key_unparent_placement_options = [
        ("BOTTOM", "Bottom", "Place unparented shape keys at the bottom of the new directory"),
        ("BELOW", "Below", "Place unparented shape keys below the folder"),
        ("ABOVE", "Above", "Place unparented shape keys above the folder"),
        ("TOP", "Top", "Place unparented shape keys at the top of the new directory")
    ]
    
    bpy.types.Scene.skp_shape_key_new_placement = bpy.props.EnumProperty(name = "New Shape Placement", items = shape_key_new_placement_options, default = "BELOW")
    bpy.types.Scene.skp_shape_key_parent_placement = bpy.props.EnumProperty(name = "Parenting Placement", items = shape_key_parent_placement_options, default = "BOTTOM")
    bpy.types.Scene.skp_shape_key_unparent_placement = bpy.props.EnumProperty(name = "Unparenting Placement", items = shape_key_unparent_placement_options, default = "ABOVE")
    bpy.types.Scene.skp_shape_key_auto_parent = bpy.props.BoolProperty(name = "Auto Parent", description = "Automatically parent new shapes to the active folder", default = True)
    bpy.types.Scene.skp_shape_key_indent_scale = bpy.props.IntProperty(name = "Indentation", default = 4, min = 0, max = 8)
    bpy.types.Scene.skp_folder_icon_pair = bpy.props.IntProperty(default = 0)
    bpy.types.Scene.skp_folder_icon_swap = bpy.props.BoolProperty(default = False)
    bpy.types.Scene.skp_driver_visible = bpy.props.BoolProperty(name = "Show Driver", default = True)
    bpy.types.Scene.skp_show_filtered_folder_contents = bpy.props.BoolProperty(name = "Show Filtered Folder Contents", description = "Show contents of a folder that is being filtered, even if its contents don't match the filter", default = True)
    bpy.types.Scene.skp_shape_key_limit_to_active = bpy.props.BoolProperty(name = "Show Active Shapes Only", description = "Only show shape keys with a value above a certain threshold", default = False)
    bpy.types.Scene.skp_filter_active_threshold = bpy.props.FloatProperty(name = "Active Threshold", description = "Only show shape keys above this value", default = 0.001, soft_min = 0.0, soft_max = 1.0)
    bpy.types.Scene.skp_filter_active_below = bpy.props.BoolProperty(name = "Flip Active Threshold", description = "Only show values lower than the threshold instead of higher", default = False)
    
    bpy.types.Scene.skp_shape_key_selections = dict()

def register():
    # Preferences
    bpy.utils.register_class(ShapeKeysPlusPreferences)
    
    # Operators
    bpy.utils.register_class(OBJECT_OT_skp_shape_key_add)
    bpy.utils.register_class(OBJECT_OT_skp_shape_key_remove)
    bpy.utils.register_class(OBJECT_OT_skp_shape_key_copy)
    bpy.utils.register_class(OBJECT_OT_skp_shape_key_move)
    bpy.utils.register_class(OBJECT_OT_skp_shape_key_select)
    bpy.utils.register_class(OBJECT_OT_skp_parent)
    bpy.utils.register_class(OBJECT_OT_skp_folder_icon)
    bpy.utils.register_class(OBJECT_OT_skp_folder_toggle)
    bpy.utils.register_class(OBJECT_OT_skp_folder_ungroup)
    bpy.utils.register_class(DRIVER_OT_skp_driver_update)
    bpy.utils.register_class(DRIVER_OT_skp_variable_add)
    bpy.utils.register_class(DRIVER_OT_skp_variable_remove)
    bpy.utils.register_class(DRIVER_OT_skp_variable_copy)
    bpy.utils.register_class(DRIVER_OT_skp_variable_move)
    
    bpy.utils.register_class(OBJECT_OT_skp_debug_folder_data)
    
    # Panels
    bpy.utils.register_class(OBJECT_PT_skp_shape_keys_plus)
    
    # Menus
    bpy.utils.register_class(MESH_UL_skp_shape_keys_plus)
    bpy.utils.register_class(MESH_MT_skp_shape_key_add_specials)
    bpy.utils.register_class(MESH_MT_skp_shape_key_copy_specials)
    bpy.utils.register_class(MESH_MT_skp_shape_key_remove_specials)
    bpy.utils.register_class(MESH_MT_skp_shape_key_other_specials)
    bpy.utils.register_class(OBJECT_MT_skp_parent)
    bpy.utils.register_class(OBJECT_MT_skp_folder_icon)
    
    extensions()
    
def unregister():
    # Menus
    bpy.utils.unregister_class(OBJECT_MT_skp_folder_icon)
    bpy.utils.unregister_class(OBJECT_MT_skp_parent)
    bpy.utils.unregister_class(MESH_MT_skp_shape_key_other_specials)
    bpy.utils.unregister_class(MESH_MT_skp_shape_key_remove_specials)
    bpy.utils.unregister_class(MESH_MT_skp_shape_key_copy_specials)
    bpy.utils.unregister_class(MESH_MT_skp_shape_key_add_specials)
    bpy.utils.unregister_class(MESH_UL_skp_shape_keys_plus)
    
    # Panels
    bpy.utils.unregister_class(OBJECT_PT_skp_shape_keys_plus)
    
    # Operators
    bpy.utils.unregister_class(OBJECT_OT_skp_debug_folder_data)
    
    bpy.utils.unregister_class(DRIVER_OT_skp_variable_move)
    bpy.utils.unregister_class(DRIVER_OT_skp_variable_copy)
    bpy.utils.unregister_class(DRIVER_OT_skp_variable_remove)
    bpy.utils.unregister_class(DRIVER_OT_skp_variable_add)
    bpy.utils.unregister_class(DRIVER_OT_skp_driver_update)
    bpy.utils.unregister_class(OBJECT_OT_skp_folder_ungroup)
    bpy.utils.unregister_class(OBJECT_OT_skp_folder_toggle)
    bpy.utils.unregister_class(OBJECT_OT_skp_folder_icon)
    bpy.utils.unregister_class(OBJECT_OT_skp_parent)
    bpy.utils.unregister_class(OBJECT_OT_skp_shape_key_select)
    bpy.utils.unregister_class(OBJECT_OT_skp_shape_key_move)
    bpy.utils.unregister_class(OBJECT_OT_skp_shape_key_copy)
    bpy.utils.unregister_class(OBJECT_OT_skp_shape_key_remove)
    bpy.utils.unregister_class(OBJECT_OT_skp_shape_key_add)
    
    # Preferences
    bpy.utils.unregister_class(ShapeKeysPlusPreferences)

if __name__ == "__main__":
    register()
