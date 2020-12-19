import os.path

from copy import deepcopy
from configparser import ConfigParser

config = ConfigParser()

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config.ini')) as file:
    config.read_file(file)

_strings_src = {
    # Generic
    'Shape Keys+': "Shape Keys+",
    'Folder': "Folder",
    'True': "True",
    'False': "False",
    'Selected (%s)': "Selected (%s)",
    'Selections': "Selections",
    'Page': "Page",
    'Driver': "Driver",
    'Expression': "Expression",
    'Type': "Type",
    'Mode': "Mode",
    'Space': "Space",
    'Object': "Object",
    'Object %s': "Object %s",
    'Bone': "Bone",
    
    # shape_keys_plus/core/folder.py
    'icon_pair[Outliner]': "Outliner",
    'icon_pair[Bold]': "Bold",
    'icon_pair[Wire]': "Wire",
    'icon_pair[Arrow]': "Arrow",
    'icon_pair[Small]': "Small",
    'icon_pair[Big]': "Big",
    'icon_pair[Pulsar]': "Pulsar",
    
    'icon_pair[Polarity]': "Polarity",
    'icon_pair[Keyframe]': "Keyframe",
    'icon_pair[Marker]': "Marker",
    'icon_pair[Diamond]': "Diamond",
    'icon_pair[Star]': "Star",
    'icon_pair[Checkbox]': "Checkbox",
    
    'icon_pair[Pin]': "Pin",
    'icon_pair[Proportional]': "Proportional",
    'icon_pair[Magnifier]': "Magnifier",
    'icon_pair[Continuity]': "Continuity",
    'icon_pair[Lock]': "Lock",
    'icon_pair[Tabs]': "Tabs",
    'icon_pair[Eye]': "Eye",
    'icon_pair[Cursor]': "Cursor",
    'icon_pair[Monitor]': "Monitor",
    'icon_pair[Camera]': "Camera",
    'icon_pair[Modifier]': "Modifier",
    'icon_pair[Mute]': "Mute",
    'icon_pair[Squeeze]': "Squeeze",
    'icon_pair[Pinch]': "Pinch",
    'icon_pair[Magnet]': "Magnet",
    'icon_pair[Precipitation]': "Precipitation",
    'icon_pair[Switch]': "Switch",
    'icon_pair[Good Read]': "Good Read",
    
    # shape_keys_plus/menus/folder_icon.py
    'menus.FolderIcon.bl_label': "Set Folder Icon",
    'menus.folder_icon.draw_menu.operator[%s (Default)]': "\"%s\" (Default)",
    'menus.folder_icon.draw_menu.operator[Swap (Active)]': "Swap (Active)",
    'menus.folder_icon.draw_menu.menu[Standard]': "Standard",
    'menus.folder_icon.draw_menu.menu[Special]': "Special",
    'menus.folder_icon.draw_menu.menu[Miscellaneous]': "Miscellaneous",
    
    # shape_keys_plus/menus/shape_key_add_context_menus.py
    'menus.ShapeKeyAddContextMenu.bl_label': "Shape Key Add Specials",
    'menus.ShapeKeyAddContextMenu.draw.operator[New Shape From Mix]': "New Shape From Mix",
    'menus.ShapeKeyAddContextMenu.draw.operator[New Folder]': "New Folder",
    
    # shape_keys_plus/menus/shape_key_copy_context_menus.py
    'menus.ShapeKeyCopyContextMenu.bl_label': "Shape Key Copy Specials",
    'menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored]': "Copy Shape Key, Mirrored",
    'menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored (Topology)]':
        "Copy Shape Key, Mirrored (Topology)",
    'menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Customized]': "Copy Shape Key, Customized",
    
    'menus.ShapeKeyCopyContextMenuSelected.draw.operator[Copy Shape Key]': "Copy Shape Key",
    
    # shape_keys_plus/menus/shape_key_other_context_menus.py
    'menus.ShapeKeyOtherContextMenu.bl_label': "Other Shape Key Specials",
    'menus.ShapeKeyOtherContextMenu.draw.menu[Set Parent...]': "Set Parent...",
    'menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key]': "Mirror Shape Key",
    'menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key (Topology)]': "Mirror Shape Key (Topology)",
    
    # shape_keys_plus/menus/shape_key_parent.py
    'menus.ShapeKeyParent.bl_label': "Set Parent",
    'menus.ShapeKeyParent.draw.operator[New Folder]': "New Folder",
    'menus.ShapeKeyParent.draw.operator[Unparent from "%s"]': "Unparent from \"%s\"",
    
    'menus.ShapeKeyParentSelected.draw.operator[Unparent from Parent]': "Unparent from Parent",
    'menus.ShapeKeyParentSelected.draw.operator[Unparent from Root]': "Unparent from Root",
    
    # shape_keys_plus/menus/shape_key_remove_context_menus.py
    'menus.ShapeKeyRemoveContextMenu.bl_label': "Shape Key Remove Specials",
    'menus.ShapeKeyRemoveContextMenu.draw.operator[Delete All Shape Keys]': "Delete All Shape Keys",
    
    'menus.ShapeKeyRemoveContextMenuSelected.draw.operator[Remove Shape Key]': "Remove Shape Key",
    
    # shape_keys_plus/operators/driver_update.py
    'operators.DriverUpdate.bl_label': "Update Driver",
    'operators.DriverUpdate.bl_description': "Force update this driver",
    
    # shape_keys_plus/operators/folder_icon.py
    'operators.ActiveFolderIcon.bl_label': "Set Active Folder Icon",
    'operators.ActiveFolderIcon.bl_description': "Sets the active folder's icon",
    'operators.ActiveFolderIcon.swap.name': "Swap",
    
    'operators.DefaultFolderIcon.bl_label': "Set Default Folder Icon",
    'operators.DefaultFolderIcon.bl_description': "Sets the default folder icon",
    'operators.DefaultFolderIcon.swap.name': "Swap",
    
    # shape_keys_plus/operators/folder_mutate.py
    'operators.FolderMutate.bl_label': "Mutate Folder",
    'operators.FolderMutate.bl_description': "Manually edit raw folder data",
    'operators.FolderMutate.children.name': "Children",
    'operators.FolderMutate.children.description':
        "The amount of children the folder has, not including children of children",
    'operators.FolderMutate.expand.name': "Expand",
    'operators.FolderMutate.expand.description': "Expand or collapse the folder",
    'operators.FolderMutate.icons.name': "Icon Pair",
    'operators.FolderMutate.icons.description':
        "The pair of icons used when the folder is expanded or collapsed. 0 = default, negative = swapped",
    
    # shape_keys_plus/operators/folder_toggle.py
    'operators.FolderToggle.bl_label': "Expand/Collapse",
    'operators.FolderToggle.bl_description': "Show or hide this folder's children",
    
    # shape_keys_plus/operators/folder_ungroup.py
    'operators.FolderUngroup.bl_label': "Ungroup Folder",
    'operators.FolderUngroup.bl_description': "Delete this folder without deleting its children",
    
    # shape_keys_plus/operators/shape_key_add.py
    'operators.ShapeKeyAdd.bl_label': "Add Shape Key",
    'operators.ShapeKeyAdd.bl_description': "Adds new shape key to the object",
    
    # shape_keys_plus/operators/shape_key_copy.py
    'operators.ShapeKeyCopy.bl_label': "Copy Shape Key",
    'operators.ShapeKeyCopy.bl_description': "Copies active or selected shape key(s)",
    
    # shape_keys_plus/operators/shape_key_mirror.py
    'operators.ShapeKeyMirror.bl_label': "Mirror Shape Key",
    'operators.ShapeKeyMirror.bl_description': "Mirrors the active or selected shape key(s) along the local X axis",
    'operators.ShapeKeyMirror.use_topology.name': "Topology Mirror",
    'operators.ShapeKeyMirror.use_topology.description':
        "Use topology based mirroring (for when both sides of mesh have matching, unique topology)",
    
    # shape_keys_plus/operators/shape_key_move.py
    'operators.ShapeKeyMove.bl_label': "Move Shape Key",
    'operators.ShapeKeyMove.bl_description': "Moves active or selected shape key(s) up/down in the list",
    'operators.ShapeKeyMove.type.items[TOP].name': "Top",
    'operators.ShapeKeyMove.type.items[UP].name': "Up",
    'operators.ShapeKeyMove.type.items[DOWN].name': "Down",
    'operators.ShapeKeyMove.type.items[BOTTOM].name': "Bottom",
    
    # shape_keys_plus/operators/shape_key_parent.py
    'operators.ShapeKeyParent.bl_label': "Set Parent",
    'operators.ShapeKeyParent.bl_description': "Sets the parent of the active or selected shape key(s)",
    'operators.ShapeKeyParent.type.items[PARENT].description': "Parents the active shape key to a folder.",
    'operators.ShapeKeyParent.type.items[UNPARENT].description': "Parents the active shape key to its grandparent.",
    'operators.ShapeKeyParent.type.items[CLEAR].description': "Unparents the active shape key completely.",
    'operators.ShapeKeyParent.type.items[NEW].description':
        "Creates a new parent folder for the active shape key, above the active shape key.",
    'operators.ShapeKeyParent.type.items[PARENT_SELECTED].description': "Parents the selected shape keys to a folder.",
    'operators.ShapeKeyParent.type.items[UNPARENT_SELECTED].description':
        "Parents each selected shape key to its respective grandparent.",
    'operators.ShapeKeyParent.type.items[CLEAR_SELECTED].description': "Unparents the selected shape keys completely.",
    'operators.ShapeKeyParent.type.items[NEW_SELECTED].description':
        "Creates a new parent folder for the selected shape keys, above the active shape key.",
    
    # shape_keys_plus/operators/shape_key_remove.py
    'operators.ShapeKeyRemove.bl_label': "Remove Shape Key",
    'operators.ShapeKeyRemove.bl_description': "Remove active or selected shape key(s) from the object",
    
    # shape_keys_plus/operators/shape_key_select.py
    'operators.ShapeKeySelect.bl_label': "Select/Deselect Shape Key",
    'operators.ShapeKeySelect.bl_description': "Select this shape key",
    
    # shape_keys_plus/operators/variable_add.py
    'operators.VariableAdd.bl_label': "Add Variable",
    'operators.VariableAdd.bl_description': "Add a new variable for this driver",
    
    # shape_keys_plus/operators/variable_copy.py
    'operators.VariableCopy.bl_label': "Copy Variable",
    'operators.VariableCopy.bl_description': "Copy this variable",
    
    # shape_keys_plus/operators/variable_move.py
    'operators.VariableMove.bl_label': "Move Variable",
    'operators.VariableMove.bl_description': "Move this variable up/down in the list",
    
    # shape_keys_plus/operators/variable_remove.py
    'operators.VariableRemove.bl_label': "Remove Variable",
    'operators.VariableRemove.bl_description': "Remove variable from the driver",
    
    # shape_keys_plus/panels/copy_customization.py
    'panels.CopyCustomization.bl_label': "Customization",
    'panels.CopyCustomization.draw.operator[Copy]': "Copy",
    'panels.CopyCustomization.draw.operator[Copy, Mirrored]': "Copy, Mirrored",
    'panels.CopyCustomization.draw.operator[Copy, Mirrored (Topology)]': "Copy, Mirrored (Topology)",
    
    # shape_keys_plus/panels/shape_key_driver.py
    'panels.ShapeKeyDriver.draw.operator[Add Variable]': "Add Variable",
    'panels.ShapeKeyDriver.draw.operator[Update Driver]': "Update Driver",
    
    # shape_keys_plus/panels/shape_keys_plus.py
    'panels.ShapeKeysPlus.draw.label[Placement]': "Placement",
    'panels.ShapeKeysPlus.draw.prop_menu_enum[Add / Copy]': "Add / Copy",
    'panels.ShapeKeysPlus.draw.prop_menu_enum[Parent]': "Parent",
    'panels.ShapeKeysPlus.draw.prop_menu_enum[Unparent]': "Unparent",
    
    'panels.ShapeKeysPlus.draw.label[Hierarchy]': "Hierarchy",
    
    'panels.ShapeKeysPlus.draw.label[%s Selected]': "%s Selected",
    'panels.ShapeKeysPlus.draw.label[Select...]': "Select...",
    'panels.ShapeKeysPlus.draw.operator[Select All]': "All",
    'panels.ShapeKeysPlus.draw.operator[Select None]': "None",
    'panels.ShapeKeysPlus.draw.operator[Select Inverse]': "Inverse",
    
    'panels.ShapeKeysPlus.draw.label[Range]': "Range",
    'panels.ShapeKeysPlus.draw.label[Range Min]': "Min",
    'panels.ShapeKeysPlus.draw.label[Range Max]': "Max",
    'panels.ShapeKeysPlus.draw.label[Relative To]': "Blend",
    
    # shape_keys_plus/__init__.py
    'AddonPreferences.hide_default.name': "Hide Default Panel",
    'AddonPreferences.hide_default.description': "Hide the default \"Shape Keys\" panel",
    'AddonPreferences.default_folder_icon_pair.name': "Style",
    'AddonPreferences.default_folder_swap_icons.name': "Swap",
    'AddonPreferences.draw.label[Default Folder Icon]': "Default Folder Icon",
    'AddonPreferences.draw.label[Shape Key Icon]': "Shape Key Icon",
    
    # shape_keys_plus/properties.py
    'properties.CopyCustomization.use_data.name': "Use Data",
    'properties.CopyCustomization.use_slider_min.name': "Use Slider Min",
    'properties.CopyCustomization.use_slider_max.name': "Use Slider Max",
    'properties.CopyCustomization.use_value.name': "Use Value",
    'properties.CopyCustomization.use_vertex_group.name': "Use Vertex Group",
    'properties.CopyCustomization.use_relative_key.name': "Use Relative Key",
    'properties.CopyCustomization.use_interpolation.name': "Use Interpolation",
    'properties.CopyCustomization.use_mute.name': "Use Mute",
    'properties.CopyCustomization.use_driver.name': "Use Driver",
    'properties.CopyCustomization.data.name': "Data",
    'properties.CopyCustomization.slider_min.name': "Slider Min",
    'properties.CopyCustomization.slider_max.name': "Slider Max",
    'properties.CopyCustomization.value.name': "Value",
    'properties.CopyCustomization.vertex_group.name': "Vertex Group",
    'properties.CopyCustomization.relative_key.name': "Relative Key",
    'properties.CopyCustomization.interpolation.name': "Interpolation",
    'properties.CopyCustomization.mute.name': "Mute",
    'properties.CopyCustomization.driver.name': "Driver",
    'properties.CopyCustomization.mirrored.name': "Mirrored",
    'properties.CopyCustomization.mirrored_topology.name': "Use Topology",
    
    'properties.KeyProperties.copy_customization.name': "Copy Customization",
    
    'properties.SceneProperties.shape_key_add_placement.name': "Add Shape Placement",
    
    'properties.SceneProperties.shape_key_add_placement.items[TOP].name': "Top",
    'properties.SceneProperties.shape_key_add_placement.items[TOP].description':
        "Place new shape keys at the top of the list",
    
    'properties.SceneProperties.shape_key_add_placement.items[ABOVE].name': "Above",
    'properties.SceneProperties.shape_key_add_placement.items[ABOVE].description':
        "Place new shape keys above the active key",
    
    'properties.SceneProperties.shape_key_add_placement.items[BELOW].name': "Below",
    'properties.SceneProperties.shape_key_add_placement.items[BELOW].description':
        "Place new shape keys below the active key",
    
    'properties.SceneProperties.shape_key_add_placement.items[BOTTOM].name': "Bottom",
    'properties.SceneProperties.shape_key_add_placement.items[BOTTOM].description':
        "Place new shape keys at the bottom of the list",
    
    'properties.SceneProperties.shape_key_parent_placement.name': "Parenting Placement",
    
    'properties.SceneProperties.shape_key_parent_placement.items[TOP].name': "Top",
    'properties.SceneProperties.shape_key_parent_placement.items[TOP].description':
        "Place newly parented shape keys at the top of the folder",
    
    'properties.SceneProperties.shape_key_parent_placement.items[BOTTOM].name': "Bottom",
    'properties.SceneProperties.shape_key_parent_placement.items[BOTTOM].description':
        "Place newly parented shape keys at the bottom of the folder",
    
    'properties.SceneProperties.shape_key_unparent_placement.name': "Unparenting Placement",
    
    'properties.SceneProperties.shape_key_unparent_placement.items[TOP].name': "Top",
    'properties.SceneProperties.shape_key_unparent_placement.items[TOP].description':
        "Place newly unparented shape keys at the top of the new directory",
    
    'properties.SceneProperties.shape_key_unparent_placement.items[ABOVE].name': "Above",
    'properties.SceneProperties.shape_key_unparent_placement.items[ABOVE].description':
        "Place newly unparented shape keys above the folder",
    
    'properties.SceneProperties.shape_key_unparent_placement.items[BELOW].name': "Below",
    'properties.SceneProperties.shape_key_unparent_placement.items[BELOW].description':
        "Place newly unparented shape keys below the folder",
    
    'properties.SceneProperties.shape_key_unparent_placement.items[BOTTOM].name': "Bottom",
    'properties.SceneProperties.shape_key_unparent_placement.items[BOTTOM].description':
        "Place newly unparented shape keys at the bottom of the new directory",
    
    'properties.SceneProperties.shape_key_auto_parent.name': "Auto Parent",
    'properties.SceneProperties.shape_key_auto_parent.description':
        "Automatically parent new shape keys to the active folder",
    
    'properties.SceneProperties.shape_key_indent_scale.name': "Indentation",
    'properties.SceneProperties.shape_key_indent_scale.description':  "Indentation of folder contents",
    
    'properties.SceneProperties.show_filtered_folder_contents.name': "Show Filtered Folder Contents",
    'properties.SceneProperties.show_filtered_folder_contents.description':
        "Show contents of a folder that is being filtered, even if its contents don't match the filter",
    
    'properties.SceneProperties.shape_key_limit_to_active.name': "Show Active Shapes Only",
    'properties.SceneProperties.shape_key_limit_to_active.description':
        "Only show shape keys with a value above a certain threshold",
    
    'properties.SceneProperties.filter_active_threshold.name': "Active Threshold",
    'properties.SceneProperties.filter_active_threshold.description': "Only show shape keys above this value",
    
    'properties.SceneProperties.filter_active_below.name': "Flip Active Threshold",
    'properties.SceneProperties.filter_active_below.description': "Only show values lower than the threshold",
}

language = config.get('Locale', 'language')
assert language in ('en_US', 'ja_JP')

if language == 'en_US':
    strings = deepcopy(_strings_src)
elif language == 'ja_JP':
    strings = deepcopy(_strings_src)
    
    # Generic
    strings['Shape Keys+'] = "シェイプキープラス"
    strings['Folder'] = "フォルダー"
    strings['True'] = "真"
    strings['False'] = "偽"
    strings['Selected (%s)'] = "選択（%s）"
    strings['Selections'] = "選択肢"
    strings['Page'] = "ページ"
    strings['Driver'] = "ドライバー"
    strings['Expression'] = "式"
    strings['Type'] = "タイプ"
    strings['Mode'] = "モード"
    strings['Space'] = "スペース"
    strings['Object'] = "オブジェクト"
    strings['Object %s'] = "オブジェクト%s"
    strings['Bone'] = "ボーン"
    
    # shape_keys_plus/core/folder.py
    strings['icon_pair[Outliner]'] = "アウトライナー"
    strings['icon_pair[Bold]'] = "ボールド"
    strings['icon_pair[Wire]'] = "ワイヤ"
    strings['icon_pair[Arrow]'] = "矢"
    strings['icon_pair[Small]'] = "小"
    strings['icon_pair[Big]'] = "大"
    strings['icon_pair[Pulsar]'] = "パルサー"
    
    strings['icon_pair[Polarity]'] = "極性"
    strings['icon_pair[Keyframe]'] = "キーフレーム"
    strings['icon_pair[Marker]'] = "マーカー"
    strings['icon_pair[Diamond]'] = "ダイヤモンド"
    strings['icon_pair[Star]'] = "スター"
    strings['icon_pair[Checkbox]'] = "チェックボックス"
    
    strings['icon_pair[Pin]'] = "釘"
    strings['icon_pair[Proportional]'] = "プロポーショナル"
    strings['icon_pair[Magnifier]'] = "拡大鏡"
    strings['icon_pair[Continuity]'] = "連続"
    strings['icon_pair[Lock]'] = "錠"
    strings['icon_pair[Tabs]'] = "タブ"
    strings['icon_pair[Eye]'] = "目"
    strings['icon_pair[Cursor]'] = "カーソル"
    strings['icon_pair[Monitor]'] = "モニター"
    strings['icon_pair[Camera]'] = "カメラ"
    strings['icon_pair[Modifier]'] = "モディファイアー"
    strings['icon_pair[Mute]'] = "ミュート"
    strings['icon_pair[Squeeze]'] = "絞る"
    strings['icon_pair[Pinch]'] = "摘む"
    strings['icon_pair[Magnet]'] = "磁石"
    strings['icon_pair[Precipitation]'] = "降水"
    strings['icon_pair[Switch]'] = "スイッチ"
    strings['icon_pair[Good Read]'] = "いい読み物"
    
    # shape_keys_plus/menus/folder_icon.py
    strings['menus.FolderIcon.bl_label'] = "フォルダにアイコンを付ける"
    strings['menus.folder_icon.draw_menu.operator[%s (Default)]'] = "「%s」（既定）"
    strings['menus.folder_icon.draw_menu.operator[Swap (Active)]'] = "裏返す（アクティブ）"
    strings['menus.folder_icon.draw_menu.menu[Standard]'] = "通常"
    strings['menus.folder_icon.draw_menu.menu[Special]'] = "特別"
    strings['menus.folder_icon.draw_menu.menu[Miscellaneous]'] = "雑多"
    
    # shape_keys_plus/menus/shape_key_add_context_menus.py
    strings['menus.ShapeKeyAddContextMenu.bl_label'] = "シェイプキー作成の特別"
    strings['menus.ShapeKeyAddContextMenu.draw.operator[New Shape From Mix]'] = "ミックスからシェイプを作成"
    strings['menus.ShapeKeyAddContextMenu.draw.operator[New Folder]'] = "フォルダを作成"
    
    # shape_keys_plus/menus/shape_key_copy_context_menus.py
    strings['menus.ShapeKeyCopyContextMenu.bl_label'] = "シェイプキー複製の特別"
    strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored]'] = "シェイプキーを鏡像複製"
    strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Mirrored (Topology)]'] = \
        "シェイプキーを鏡像複製（トポロジー）"
    strings['menus.ShapeKeyCopyContextMenu.draw.operator[Copy Shape Key, Customized]'] = "シェイプキーを調整複製"
    
    strings['menus.ShapeKeyCopyContextMenuSelected.draw.operator[Copy Shape Key]'] = "シェイプキーを複製"
    
    # shape_keys_plus/menus/shape_key_other_context_menus.py
    strings['menus.ShapeKeyOtherContextMenu.bl_label'] = "雑多特別"
    strings['menus.ShapeKeyOtherContextMenu.draw.menu[Set Parent...]'] = "親を改める..."
    strings['menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key]'] = "シェイプキーを鏡像反転"
    strings['menus.ShapeKeyOtherContextMenu.draw.operator[Mirror Shape Key (Topology)]'] = \
        "シェイプキーを鏡像反転（トポロジー）"
    
    # shape_keys_plus/menus/shape_key_parent.py
    strings['menus.ShapeKeyParent.bl_label'] = "親を改める"
    strings['menus.ShapeKeyParent.draw.operator[New Folder]'] = "新作成フォルダー"
    strings['menus.ShapeKeyParent.draw.operator[Unparent from "%s"]'] = "「%s」親に関係を削除"
    
    strings['menus.ShapeKeyParentSelected.draw.operator[Unparent from Parent]'] = "親に関係を削除"
    strings['menus.ShapeKeyParentSelected.draw.operator[Unparent from Root]'] = "根に関係を削除"
    
    # shape_keys_plus/menus/shape_key_remove_context_menus.py
    strings['menus.ShapeKeyRemoveContextMenu.bl_label'] = "シェイプキー削除の特別"
    strings['menus.ShapeKeyRemoveContextMenu.draw.operator[Delete All Shape Keys]'] = "全てシェイプキーを削除"
    
    strings['menus.ShapeKeyRemoveContextMenuSelected.draw.operator[Remove Shape Key]'] = "シェイプキーを削除"
    
    # shape_keys_plus/operators/driver_update.py
    strings['operators.DriverUpdate.bl_label'] = "ドライバを更新 (Update Driver)"
    strings['operators.DriverUpdate.bl_description'] = "このドライバを強引更新する"
    
    # shape_keys_plus/operators/folder_icon.py
    strings['operators.ActiveFolderIcon.bl_label'] = "アクティブフォルダのアイコンを改める (Set Active Folder Icon)"
    strings['operators.ActiveFolderIcon.bl_description'] = "アクティブフォルダのアイコンを改めます"
    strings['operators.ActiveFolderIcon.swap.name'] = "裏返す"
    
    strings['operators.DefaultFolderIcon.bl_label'] = "フォルダの既定アイコンを改める (Set Default Folder Icon)"
    strings['operators.DefaultFolderIcon.bl_description'] = "フォルダの既定アイコンを改めます"
    strings['operators.DefaultFolderIcon.swap.name'] = "裏返す"
    
    # shape_keys_plus/operators/folder_mutate.py
    strings['operators.FolderMutate.bl_label'] = "フォルダを変化 (Mutate Folder)"
    strings['operators.FolderMutate.bl_description'] = "フォルダの生のデータを、手動変化します"
    strings['operators.FolderMutate.children.name'] = "子たち"
    strings['operators.FolderMutate.children.description'] = "フォルダの子たちの量です（子たちの子たちを含めていません）"
    strings['operators.FolderMutate.expand.name'] = "開けている"
    strings['operators.FolderMutate.expand.description'] = "フォルダを開けるか閉めます"
    strings['operators.FolderMutate.icons.name'] = "アイコンの対"
    strings['operators.FolderMutate.icons.description'] = \
        "フォルダの開けているか閉めている場合に、使うアイコンの対（０＝既定、負数＝裏返す）"
    
    # shape_keys_plus/operators/folder_toggle.py
    strings['operators.FolderToggle.bl_label'] = "開ける・閉める (Expand/Collapse)"
    strings['operators.FolderToggle.bl_description'] = "フォルダの子供を晒すか隠します"
    
    # shape_keys_plus/operators/folder_ungroup.py
    strings['operators.FolderUngroup.bl_label'] = "フォルダを解除 (Ungroup Folder)"
    strings['operators.FolderUngroup.bl_description'] = "子たちを削除しないで、このフォルダを削除します"
    
    # shape_keys_plus/operators/shape_key_add.py
    strings['operators.ShapeKeyAdd.bl_label'] = "シェイプキーを作成 (Add Shape Key)"
    strings['operators.ShapeKeyAdd.bl_description'] = "空のシェイプキーを作成します"
    
    # shape_keys_plus/operators/shape_key_copy.py
    strings['operators.ShapeKeyCopy.bl_label'] = "シェイプキーを複製 (Copy Shape Key)"
    strings['operators.ShapeKeyCopy.bl_description'] = "アクティブか選択したシェイプキーを複製します"
    
    # shape_keys_plus/operators/shape_key_mirror.py
    strings['operators.ShapeKeyMirror.bl_label'] = "シェイプキーを鏡像反転 (Mirror Shape Key)"
    strings['operators.ShapeKeyMirror.bl_description'] = "アクティブか選択したシェイプキーをロカルX軸で鏡像反転します"
    strings['operators.ShapeKeyMirror.use_topology.name'] = "トポロジーによる鏡像反転"
    strings['operators.ShapeKeyMirror.use_topology.description'] = "メッシュの両側のトポロジーが一致の場合にための使います"
    
    # shape_keys_plus/operators/shape_key_move.py
    strings['operators.ShapeKeyMove.bl_label'] = "シェイプキーを移動 (Move Shape Key)"
    strings['operators.ShapeKeyMove.bl_description'] = "列記で、アクティブか選択したシェイプキーを上げる・下ろす移動します"
    strings['operators.ShapeKeyMove.type.items[TOP].name'] = "頂"
    strings['operators.ShapeKeyMove.type.items[UP].name'] = "上"
    strings['operators.ShapeKeyMove.type.items[DOWN].name'] = "下"
    strings['operators.ShapeKeyMove.type.items[BOTTOM].name'] = "底"
    
    # shape_keys_plus/operators/shape_key_parent.py
    strings['operators.ShapeKeyParent.bl_label'] = "親を改める (Set Parent)"
    strings['operators.ShapeKeyParent.bl_description'] = "アクティブか選択したシェイプキーの親を改めます"
    strings['operators.ShapeKeyParent.type.items[PARENT].description'] = "フォルダにアクティブシェイプキーを親します。"
    strings['operators.ShapeKeyParent.type.items[UNPARENT].description'] = "上の親にアクティブシェイプキーを親します。"
    strings['operators.ShapeKeyParent.type.items[CLEAR].description'] = "全親からアクティブシェイプキーを外します。"
    strings['operators.ShapeKeyParent.type.items[NEW].description'] = \
        "アクティブシェイプキーための、アクティブシェイプキーの上に新親フォルダを作成します。"
    strings['operators.ShapeKeyParent.type.items[PARENT_SELECTED].description'] = \
        "フォルダに選択したシェイプキーを親します。"
    strings['operators.ShapeKeyParent.type.items[UNPARENT_SELECTED].description'] = \
        "それぞれの上の親に選択したシェイプキーを親します。"
    strings['operators.ShapeKeyParent.type.items[CLEAR_SELECTED].description'] = \
        "全親から選択したシェイプキーを外します。"
    strings['operators.ShapeKeyParent.type.items[NEW_SELECTED].description'] = \
        "選択したシェイプキーための、アクティブシェイプキーの上に新親フォルダを作成します。"
    
    # shape_keys_plus/operators/shape_key_remove.py
    strings['operators.ShapeKeyRemove.bl_label'] = "シェイプキーを削除 (Remove Shape Key)"
    strings['operators.ShapeKeyRemove.bl_description'] = "アクティブか選択したシェイプキーを削除します"
    
    # shape_keys_plus/operators/shape_key_select.py
    strings['operators.ShapeKeySelect.bl_label'] = "シェイプキーを選択・選択解除 (Select/Deselect Shape Key)"
    strings['operators.ShapeKeySelect.bl_description'] = "このシェイプキーを選択します"
    
    # shape_keys_plus/operators/variable_add.py
    strings['operators.VariableAdd.bl_label'] = "変数を作成 (Add Variable)"
    strings['operators.VariableAdd.bl_description'] = "このドライバのための新変数を作成します"
    
    # shape_keys_plus/operators/variable_copy.py
    strings['operators.VariableCopy.bl_label'] = "変数を複製 (Copy Variable)"
    strings['operators.VariableCopy.bl_description'] = "この変数を複製します"
    
    # shape_keys_plus/operators/variable_move.py
    strings['operators.VariableMove.bl_label'] = "変数を移動 (Move Variable)"
    strings['operators.VariableMove.bl_description'] = "列記で、この変数を上げる・下ろす移動します"
    
    # shape_keys_plus/operators/variable_remove.py
    strings['operators.VariableRemove.bl_label'] = "変数を削除 (Remove Variable)"
    strings['operators.VariableRemove.bl_description'] = "ドライバから変数を削除します"
    
    # shape_keys_plus/panels/copy_customization.py
    strings['panels.CopyCustomization.bl_label'] = "調整"
    strings['panels.CopyCustomization.draw.operator[Copy]'] = "複製"
    strings['panels.CopyCustomization.draw.operator[Copy, Mirrored]'] = "鏡像複製"
    strings['panels.CopyCustomization.draw.operator[Copy, Mirrored (Topology)]'] = "鏡像複製（トポロジー）"
    
    # shape_keys_plus/panels/shape_key_driver.py
    strings['panels.ShapeKeyDriver.draw.operator[Add Variable]'] = "変数を作成"
    strings['panels.ShapeKeyDriver.draw.operator[Update Driver]'] = "ドライバを更新"
    
    # shape_keys_plus/panels/shape_keys_plus.py
    strings['panels.ShapeKeysPlus.draw.label[Placement]'] = "位置調整"
    strings['panels.ShapeKeysPlus.draw.prop_menu_enum[Add / Copy]'] = "新しい・複製"
    strings['panels.ShapeKeysPlus.draw.prop_menu_enum[Parent]'] = "フォルダまで"
    strings['panels.ShapeKeysPlus.draw.prop_menu_enum[Unparent]'] = "フォルダから"
    
    strings['panels.ShapeKeysPlus.draw.label[Hierarchy]'] = "階層構造"
    
    strings['panels.ShapeKeysPlus.draw.label[%s Selected]'] = "%s個選"
    strings['panels.ShapeKeysPlus.draw.label[Select...]'] = "...を選ぶ"
    strings['panels.ShapeKeysPlus.draw.operator[Select All]'] = "全"
    strings['panels.ShapeKeysPlus.draw.operator[Select None]'] = "無"
    strings['panels.ShapeKeysPlus.draw.operator[Select Inverse]'] = "逆"
    
    strings['panels.ShapeKeysPlus.draw.label[Range]'] = "範囲"
    strings['panels.ShapeKeysPlus.draw.label[Range Min]'] = "最小"
    strings['panels.ShapeKeysPlus.draw.label[Range Max]'] = "最大"
    strings['panels.ShapeKeysPlus.draw.label[Relative To]'] = "相対"
    
    # shape_keys_plus/__init__.py
    strings['AddonPreferences.hide_default.name'] = "既定パネルを隠"
    strings['AddonPreferences.hide_default.description'] = "既定「シェイプキー」パネルを隠します"
    strings['AddonPreferences.default_folder_icon_pair.name'] = "様式"
    strings['AddonPreferences.default_folder_swap_icons.name'] = "裏返す"
    strings['AddonPreferences.draw.label[Default Folder Icon]'] = "フォルダの既定アイコン"
    strings['AddonPreferences.draw.label[Shape Key Icon]'] = "シェイプキーのアイコン"
    
    # shape_keys_plus/properties.py
    strings['properties.CopyCustomization.use_data.name'] = "データを使う"
    strings['properties.CopyCustomization.use_slider_min.name'] = "範囲最小を使う"
    strings['properties.CopyCustomization.use_slider_max.name'] = "範囲最大を使う"
    strings['properties.CopyCustomization.use_value.name'] = "値を使う"
    strings['properties.CopyCustomization.use_vertex_group.name'] = "頂点グループを使う"
    strings['properties.CopyCustomization.use_relative_key.name'] = "相対キーを使う"
    strings['properties.CopyCustomization.use_interpolation.name'] = "捕間を使う"
    strings['properties.CopyCustomization.use_mute.name'] = "無効化を使う"
    strings['properties.CopyCustomization.use_driver.name'] = "ドライバーを使う"
    strings['properties.CopyCustomization.data.name'] = "データ"
    strings['properties.CopyCustomization.slider_min.name'] = "範囲最小"
    strings['properties.CopyCustomization.slider_max.name'] = "範囲最大"
    strings['properties.CopyCustomization.value.name'] = "値"
    strings['properties.CopyCustomization.vertex_group.name'] = "頂点グループ"
    strings['properties.CopyCustomization.relative_key.name'] = "相対キー"
    strings['properties.CopyCustomization.interpolation.name'] = "補間"
    strings['properties.CopyCustomization.mute.name'] = "無効化"
    strings['properties.CopyCustomization.driver.name'] = "ドライバー"
    strings['properties.CopyCustomization.mirrored.name'] = "鏡像"
    strings['properties.CopyCustomization.mirrored_topology.name'] = "トポロジを使う"
    
    strings['properties.KeyProperties.copy_customization.name'] = "複製調整"
    
    strings['properties.SceneProperties.shape_key_add_placement.name'] = "新シェイプキーの位置"
    strings['properties.SceneProperties.shape_key_add_placement.items[TOP].name'] = "頂"
    strings['properties.SceneProperties.shape_key_add_placement.items[TOP].description'] = \
        "列記の頂上に新シェイプキーを位置します"
    strings['properties.SceneProperties.shape_key_add_placement.items[ABOVE].name'] = "上"
    strings['properties.SceneProperties.shape_key_add_placement.items[ABOVE].description'] = \
        "アクティブシェイプキーの上に新シェイプキーを位置します"
    strings['properties.SceneProperties.shape_key_add_placement.items[BELOW].name'] = "下"
    strings['properties.SceneProperties.shape_key_add_placement.items[BELOW].description'] = \
        "アクティブシェイプキーの下に新シェイプキーを位置します"
    strings['properties.SceneProperties.shape_key_add_placement.items[BOTTOM].name'] = "底"
    strings['properties.SceneProperties.shape_key_add_placement.items[BOTTOM].description'] = \
        "列記の底に新シェイプキーを位置します"
    
    strings['properties.SceneProperties.shape_key_parent_placement.name'] = "親の接続位置"
    strings['properties.SceneProperties.shape_key_parent_placement.items[TOP].name'] = "頂"
    strings['properties.SceneProperties.shape_key_parent_placement.items[TOP].description'] = \
        "フォルダの頂上に新しく親するシェイプキーを位置します"
    strings['properties.SceneProperties.shape_key_parent_placement.items[BOTTOM].name'] = "底"
    strings['properties.SceneProperties.shape_key_parent_placement.items[BOTTOM].description'] = \
        "フォルダの底に新しく親するシェイプキーを位置します"
    
    strings['properties.SceneProperties.shape_key_unparent_placement.name'] = "親の解除位置"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[TOP].name'] = "頂"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[TOP].description'] = \
        "新ディレクトリの頂上に新しく親外すシェイプキーを位置します"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[ABOVE].name'] = "上"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[ABOVE].description'] = \
        "フォルダの上に新しく親外すシェイプキーを位置します"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[BELOW].name'] = "下"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[BELOW].description'] = \
        "フォルダの下に新しく親外すシェイプキーを位置します"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[BOTTOM].name'] = "底"
    strings['properties.SceneProperties.shape_key_unparent_placement.items[BOTTOM].description'] = \
        "新ディレクトリの底に新しく親外すシェイプキーを位置します"
    
    strings['properties.SceneProperties.shape_key_auto_parent.name'] = "オート親子関係"
    strings['properties.SceneProperties.shape_key_auto_parent.description'] = \
        "アクティブフォルダに、新シェイプキーを自動的に親の接続します"
    
    strings['properties.SceneProperties.shape_key_indent_scale.name'] = "字下げ"
    strings['properties.SceneProperties.shape_key_indent_scale.description'] = "フォルダの内容ための字下げです"
    
    strings['properties.SceneProperties.show_filtered_folder_contents.name'] = "濾しているフォルダ内容を晒"
    strings['properties.SceneProperties.show_filtered_folder_contents.description'] = \
        "たとえ内容を濾過に一致しなくても濾しているフォルダの内容を晒します"
    
    strings['properties.SceneProperties.shape_key_limit_to_active.name'] = "アクティブシェイプだけを晒"
    strings['properties.SceneProperties.shape_key_limit_to_active.description'] = \
        "特定閾値以上値のシェイプキーだけを晒します"
    
    strings['properties.SceneProperties.filter_active_threshold.name'] = "アクティブ閾値"
    strings['properties.SceneProperties.filter_active_threshold.description'] = "この値以上のシェイプキーだけを晒します"
    
    strings['properties.SceneProperties.filter_active_below.name'] = "アクティブ閾値を逆"
    strings['properties.SceneProperties.filter_active_below.description'] = "閾値未満の値だけを晒します"
