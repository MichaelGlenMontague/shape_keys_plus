Shape Keys+
===========
###### Shape Keys Plus v1.2

A [Blender](https://www.blender.org/) add-on that replaces the default ***Shape Keys*** panel with ***Shape Keys+,*** a plus-size panel containing extra features for creating, sorting, viewing, and driving shape keys.

![Imgur](https://i.imgur.com/ZEq0D72.png)

## Documentation

* [Folders](#folders)
* [Copying](#copying)
* [Drivers](#drivers)
* [Filtering](#filtering)

<a name="folders"/>

## Folders

The main feature of ***Shape Keys+*** is the ability to create folders for easy sorting of shape keys. A shape key folder is a shape key in itself, though few things that work for normal shape keys will also work for folders.

Since a folder is a shape key, it must be created from the drop-down menu next to the **Add Shape** operator (*plus* icon) on the right-hand side of the panel. This will create an empty folder at the location specified by the **Add/Copy** setting of the **Placement** box at the top of the panel.

#### Parenting and unparenting

Shape keys and folders may be parented to and unparented from folders. This is done by selecting the large **Specials** drop-down menu on the right and highlighting **Set Parent to**.

#### Removing a folder

To delete a folder without also deleting all its contents, click the *X* icon on the right. The standard **Remove Shape** operator (*minus* icon) will delete both the folder and its contents.

<a name="copying"/>

## Copying

Without ***Shape Keys+,*** copying a shape key is a tedious task that requires you to manually hide all but one shape key and set all of its values to default in order to create an "image" of your model, then use the **New Shape From Mix** operator to turn that "image" into a new shape key.

With ***Shape Keys+,*** this is all done with one button. On the right-hand side of the panel, there is a button with an icon of a *clipboard* on it. This button is the standard **Copy Shape** operator, which works for regular shape keys and shape key folders, including the contents of said folder.

#### What the "Copy Shape" operator does:
* Copies the **raw shape key data**, ignoring modifiers such as drivers, vertex group, visibility state, and current value
* Copies the **name** of the shape key and flips the ".L"/".R" suffix if ***Mirrored*** is selected from the drop-down menu
* Copies the **range** of the shape key value (**min/max** sliders)
* Copies the shape key **value** at the time of copying
* Copies the shape key's reference to its **vertex group**
* Copies the shape key's reference to its **relative key** (also known as **"Basis"** by default)
* Copies the shape key's **interpolation** value (a setting used when **Relative** mode is disabled)
* Copies the shape key's **visibility** state
* Does all of the above for **folders** and their contents as well

#### What it doesn't do:
* Copies the shape key's **driver**
* Copies the shape key's **animation** data

<a name="drivers"/>

## Drivers

When a driver exists for a shape key, its properties will appear at the bottom of the ***Shape Keys+*** panel for easy access. This section of the panel contains almost all features of the **Drivers** tab from Blender's **Graph Editor**. It lacks features from the **Modifiers** tab, however.

#### Variables

In the ***Shape Keys+*** driver editor, variables also have extra features. Here, they can be freely moved up and down, as well as to the top and bottom of the list. Like shape keys, driver variables can also be copied using the button with the *clipboard* icon.

<a name="filtering"/>

## Filtering

The obscure *expand/collapse* icon at the bottom of the shape keys list is a button that toggles filtering options. In addition to the default ***Shape Keys*** panel's filtering options, ***Shape Keys+*** includes an option to only show shape keys above or below a certain value, as well as an option to skip filtering of folder contents when the folder itself has a valid name.
