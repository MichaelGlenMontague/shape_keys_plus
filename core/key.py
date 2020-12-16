import bpy

from bpy.app.translations import pgettext_data

from shape_keys_plus import core
from shape_keys_plus import memory


def is_folder(key):
    return key.vertex_group.startswith(core.folder.blocks['prefix']['id'] + ".")


def is_selected(key):
    return str(key.id_data.key_blocks.find(key)) in key.id_data.shape_keys_plus.selections


def get_selected_indices():
    obj = bpy.context.object
    
    if not obj or not obj.data.shape_keys:
        return []
    
    selections = obj.data.shape_keys.shape_keys_plus.selections
    
    return sorted(int(x.name) for x in selections if x.name.isdigit())


def get_selected():
    """Returns a list of selected bpy.types.ShapeKey."""
    # Requires no existence check, because the same one already exists in get_selected_indices().
    return [bpy.context.object.data.shape_keys.key_blocks[index] for index in get_selected_indices()]


def get_driver(key, fcurve=False):
    data_path = "key_blocks[\"%s\"].value" % key.name
    anim = key.id_data.animation_data
    
    if anim and anim.drivers:
        for fc in anim.drivers:
            if fc.data_path == data_path:
                return fc if fcurve else fc.driver
    
    return None


def add(type='DEFAULT'):
    obj = bpy.context.object
    
    # Add the key.
    if type == 'FROM_MIX':
        new_key = obj.shape_key_add(from_mix=True)
    elif type == 'FROM_MIX_SELECTED' and obj.data.shape_keys:
        exclude = []
        
        for i, key in enumerate(obj.data.shape_keys.key_blocks):
            if not is_selected(key) and not key.mute:
                key.mute = True
                exclude.append(i)
        
        new_key = obj.shape_key_add(from_mix=True)
        
        for i in exclude:
            obj.data.shape_keys.key_blocks[i].mute = False
        
        deselect()
    else:
        new_key = obj.shape_key_add(from_mix=False)
    
    # Only create a reference to shape_keys.key_blocks after a key is sure to exist, so that shape_keys is not None.
    key_blocks = obj.data.shape_keys.key_blocks
    folder_count = len([key for key in key_blocks if is_folder(key)])
    
    translate_new_dataname = bpy.context.preferences.view.use_translate_new_dataname
    
    if type == 'FOLDER':
        new_key.name = (core.strings['Folder'] if translate_new_dataname else "Folder") + " " + str(folder_count + 1)
        new_key.vertex_group = core.folder.generate()
    else:
        if len(key_blocks) == 1:
            new_key.name = pgettext_data("Basis")
        else:
            new_key.name = pgettext_data("Key") + " " + str(
                len(key_blocks) - folder_count - (not is_folder(key_blocks[0])))
    
    return new_key


def select(i, v):
    obj = bpy.context.object
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    selections = shape_keys.shape_keys_plus.selections
    
    if type(i) == bpy.types.ShapeKey:
        key = i
        i = key_blocks.find(key.name)
    elif type(i) == str:
        assert i in key_blocks, "Invalid name given for shape key selection."
        key = key_blocks[i]
        i = key_blocks.find(key.name)
    elif type(i) == int:
        key = core.utils.get(key_blocks, i, None)
        assert key, "Invalid index given for shape key selection."
    
    if i <= 0:
        return
    
    i = str(i)
    
    if v:
        core.utils.get(selections, i, selections.add()).name = i
    else:
        while i in selections:
            selections.remove(selections.find(i))


def deselect():
    """Deselects all shape keys and returns a list of names to be passed as the argument to reselect()."""
    selections = [key.name for key in get_selected()]
    bpy.context.object.data.shape_keys.shape_keys_plus.selections.clear()
    return selections


def reselect(selections):
    """Selects the shape keys from the list of names in `selections`, such as those returned by deselect()."""
    for name in selections:
        # Check if the shape key hasn't been deleted since the `selections` list was created.
        if name in bpy.context.object.data.shape_keys.key_blocks:
            select(name, True)


def copy(original_key, mirror=0, custom=False):
    obj = bpy.context.object
    shape_keys = obj.data.shape_keys
    key_blocks = shape_keys.key_blocks
    anim = shape_keys.animation_data
    cc = obj.data.shape_keys.shape_keys_plus.copy_customization
    is_folder = core.key.is_folder(original_key)
    
    # Store original values.
    old_data = [data.co for data in original_key.data]
    old_name = original_key.name
    old_slider_min = original_key.slider_min
    old_slider_max = original_key.slider_max
    old_value = original_key.value
    old_vertex_group = original_key.vertex_group
    old_relative_key = getattr(original_key.relative_key, 'name', "")
    old_interpolation = original_key.interpolation
    old_mute = original_key.mute
    
    new_key = obj.shape_key_add(from_mix=False)
    
    # Copy the original shape key's raw data to the new shape key.
    if custom and cc.use_data:
        if cc.data:
            for i, vec in enumerate([data.co for data in key_blocks[cc.data].data]):
                new_key.data[i].co[:] = vec
    else:
        for i, vec in enumerate(old_data):
            new_key.data[i].co[:] = vec
    
    # Select the new key, which was sent to the bottom.
    obj.active_shape_key_index = len(key_blocks) - 1
    
    new_name = old_name
    
    if mirror > 0:
        bpy.ops.object.shape_key_mirror(use_topology=mirror == 2)
        
        if old_name.endswith(".L"):
            new_name = old_name[:-2] + ".R"
        elif old_name.endswith(".R"):
            new_name = old_name[:-2] + ".L"
    
    new_relative_key = old_relative_key if (not custom or not cc.use_relative_key) else cc.relative_key
    
    # Copy original values.
    new_key.name = new_name
    new_key.slider_min = old_slider_min if (not custom or not cc.use_slider_min) else cc.slider_min
    new_key.slider_max = old_slider_max if (not custom or not cc.use_slider_max) else cc.slider_max
    new_key.value = old_value if (not custom or not cc.use_value) else cc.value
    new_key.vertex_group = old_vertex_group if is_folder or (not custom or not cc.use_vertex_group) else cc.vertex_group
    new_key.relative_key = key_blocks[new_relative_key] if new_relative_key else key_blocks[0]
    new_key.interpolation = old_interpolation if (not custom or not cc.use_interpolation) else cc.interpolation
    new_key.mute = old_mute if (not custom or not cc.use_mute) else cc.mute
    
    if anim and anim.drivers:
        data_path = "key_blocks[\"%s\"].value" % new_key.name
        driver = None
        
        # Remove all conflicting drivers to make room for the copied one.
        for fc in anim.drivers:
            if fc.data_path == data_path:
                anim.drivers.remove(fc)
        
        # Copy the driver.
        if custom and cc.use_driver:
            driver = get_driver(key_blocks[cc.driver], fcurve=True) if cc.driver else None
        else:
            driver = get_driver(key_blocks[old_name], fcurve=True)
        
        if driver:
            new_driver = anim.drivers.from_existing(src_driver=driver)
            new_driver.data_path = data_path
    
    return new_key
