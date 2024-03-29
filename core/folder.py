import bpy

from .. import core

import re


blocks = {
    # This goes at the beginning of a shape key's vertex group to identify it as a folder.
    'prefix': {
        'id': "SKP"
    },
    # Number of child shape keys under the folder, not including children of children.
    'children': {
        'id': "C",
        'default': 0
    },
    # The closed/open state of the folder.
    'expand': {
        'id': "E",
        'default': 1
    },
    # The ID for the icon pair used when the folder is expanded or collapsed.
    # A negative value will swap the icons, and 0 will use the default settings.
    'icons': {
        'id': "I",
        'default': 0
    }
}

icon_pairs_standard = (
    ('DISCLOSURE_TRI_DOWN', 'DISCLOSURE_TRI_RIGHT', core.strings['icon_pair[Outliner]'], "", 1),
    ('TRIA_DOWN', 'TRIA_RIGHT', core.strings['icon_pair[Bold]'], "", 2),
    ('DOWNARROW_HLT', 'RIGHTARROW', core.strings['icon_pair[Wire]'], "", 3),
    ('SORT_ASC', 'FORWARD', core.strings['icon_pair[Arrow]'], "", 4),
    ('LAYER_ACTIVE', 'LAYER_USED', core.strings['icon_pair[Small]'], "", 5),
    ('RADIOBUT_ON', 'RADIOBUT_OFF', core.strings['icon_pair[Big]'], "", 6),
    ('DOT', 'REC', core.strings['icon_pair[Pulsar]'], "", 7),
)

icon_pairs_special = (
    ('REMOVE', 'ADD', core.strings['icon_pair[Polarity]'], "", 8),
    ('KEYFRAME_HLT', 'KEYFRAME', core.strings['icon_pair[Keyframe]'], "", 9),
    ('MARKER_HLT', 'MARKER', core.strings['icon_pair[Marker]'], "", 10),
    ('PMARKER_ACT', 'PMARKER_SEL', core.strings['icon_pair[Diamond]'], "", 11),
    ('SOLO_ON', 'SOLO_OFF', core.strings['icon_pair[Star]'], "", 12),
    ('CHECKBOX_HLT', 'CHECKBOX_DEHLT', core.strings['icon_pair[Checkbox]'], "", 13),
)

icon_pairs_miscellaneous = (
    ('PINNED', 'UNPINNED', core.strings['icon_pair[Pin]'], "", 14),
    ('PROP_ON', 'PROP_OFF', core.strings['icon_pair[Proportional]'], "", 15),
    ('ZOOM_OUT', 'ZOOM_IN', core.strings['icon_pair[Magnifier]'], "", 16),
    ('MESH_PLANE', 'SHADING_BBOX', core.strings['icon_pair[Continuity]'], "", 17),
    ('DECORATE_UNLOCKED', 'DECORATE_LOCKED', core.strings['icon_pair[Lock]'], "", 18),
    ('RESTRICT_COLOR_ON', 'RESTRICT_COLOR_OFF', core.strings['icon_pair[Tabs]'], "", 19),
    ('HIDE_OFF', 'HIDE_ON', core.strings['icon_pair[Eye]'], "", 20),
    ('RESTRICT_SELECT_OFF', 'RESTRICT_SELECT_ON', core.strings['icon_pair[Cursor]'], "", 21),
    ('RESTRICT_VIEW_OFF', 'RESTRICT_VIEW_ON', core.strings['icon_pair[Monitor]'], "", 22),
    ('RESTRICT_RENDER_OFF', 'RESTRICT_RENDER_ON', core.strings['icon_pair[Camera]'], "", 23),
    ('MODIFIER_ON', 'MODIFIER_OFF', core.strings['icon_pair[Modifier]'], "", 24),
    ('MUTE_IPO_ON', 'MUTE_IPO_OFF', core.strings['icon_pair[Mute]'], "", 25),
    ('SMOOTHCURVE', 'SPHERECURVE', core.strings['icon_pair[Squeeze]'], "", 26),
    ('SHARPCURVE', 'ROOTCURVE', core.strings['icon_pair[Pinch]'], "", 27),
    ('SNAP_ON', 'SNAP_OFF', core.strings['icon_pair[Magnet]'], "", 28),
    ('FREEZE', 'MATFLUID', core.strings['icon_pair[Precipitation]'], "", 29),
    ('ALIGN_TOP', 'ALIGN_BOTTOM', core.strings['icon_pair[Switch]'], "", 30),
    ('TEXT', 'ASSET_MANAGER', core.strings['icon_pair[Good Read]'], "", 31)
)

icon_pairs = \
    icon_pairs_standard[:] + \
    icon_pairs_special[:] + \
    icon_pairs_miscellaneous[:]


def get_icon_pair(id):
    return next((p for p in icon_pairs if p[-1] == abs(id)), icon_pairs[0])


def get_active_icon(folder):
    icon_pair_value = get_block_value(folder, 'icons')
    expand_value = get_block_value(folder, 'expand')
    
    if icon_pair_value != 0:
        icon_pair = get_icon_pair(icon_pair_value)
        swap = icon_pair_value < 0
    else:
        icon_pair = get_icon_pair(core.preferences.default_folder_icon_pair)
        swap = core.preferences.default_folder_swap_icons
    
    return icon_pair[swap if expand_value else not swap]


def generate(children=None, expand=None, icons=None):
    children = children if children is not None else blocks['children']['default']
    expand = expand if expand is not None else blocks['expand']['default']
    icons = icons if icons is not None else blocks['icons']['default']
    
    return ".".join((
        blocks['prefix']['id'],
        blocks['children']['id'] + str(children),
        blocks['expand']['id'] + str(expand),
        blocks['icons']['id'] + str(icons)
    ))


def toggle(key, expand=None):
    set_block_value(key, 'expand', (1 - int(get_block_value(key, 'expand'))) if expand is None else int(expand))


def get_blocks(key):
    assert core.key.is_folder(key), "Attempted to get folder block data from a normal shape key."
    return key.vertex_group.split(".")


def set_blocks(key, blocks):
    assert core.key.is_folder(key), "Attempted to set folder block data to a normal shape key."
    key.vertex_group = ".".join(blocks)


def get_block_value(key, name):
    return int(re.sub(r'[^-\d]', "", get_blocks(key)[find_block(key, name)]))


def set_block_value(key, name, value):
    assert core.key.is_folder(key), "Attempted to set folder block data to a normal shape key."
    
    blocks = get_blocks(key)
    index = find_block(key, name)
    blocks[index] = re.sub(r'[^A-Z]', "", blocks[index]) + str(value)
    set_blocks(key, blocks)


def shift_block_value(key, name, value):
    set_block_value(key, name, get_block_value(key, name) + value)


def get_block(key, id):
    return next((b for b in get_blocks(key) if get_block_id(b) == id), None)


def has_block(key, id):
    return get_block(key, id) is not None


def find_block(key, name):
    return next((i for i, b in enumerate(get_blocks(key)) if re.sub(r"[^A-Z]", "", b) == blocks[name]['id']), -1)


def get_capacity(key, recursive=True):
    capacity = 0
    
    if not core.key.is_folder(key):
        return capacity
    elif not recursive:
        return core.folder.get_block_value(key, 'children')
    
    key_blocks = key.id_data.key_blocks
    
    start = key_blocks.find(key.name) + 1
    stop = start + get_block_value(key, 'children')
    
    i = start
    
    while i < stop:
        if len(key_blocks) > i:
            child = key_blocks[i]
            
            capacity += 1
            
            if core.key.is_folder(child):
                stop += get_block_value(child, 'children')
            
            i += 1
        else:
            break # Folder Mutation Fail-Safe
    
    return capacity


def get_children(key, recursive=True):
    children = []
    
    if not core.key.is_folder(key):
        return children
    
    key_blocks = key.id_data.key_blocks
    
    start = key_blocks.find(key.name) + 1
    stop = start + get_capacity(key)
    i = start
    
    while i < stop:
        if len(key_blocks) > i:
            child = key_blocks[i]
            children.append(child)
            
            i += 1 + ((not recursive) * get_capacity(child))
        else:
            break # Folder Mutation Fail-Safe
    
    return children
