import bpy

from . import core

import itertools


class Tree:
    """
    The tree hierarchy of a single object's shape keys.
    
    The root directory is a list, `Tree.tree`, containing each key's name. If a shape key is a folder, it becomes
    another list with its own name at index 0, and the names of its children appended to it. If any of these children
    are also folders, they too become lists, and so on.
    
    `Tree.get_*` methods retrieve data from `Tree.cache`. These are meant to be used in polls,
    so that expensive functions aren't being called on idle frames.
    
    `Tree.active` is the `Tree` that is created on each poll where a change is detected in the object's shape keys.
    
    After calling a method that modifies the hierarchy, `Tree.forget()` will also be called, to initialize the cache.
    
    At the end of tree manipulation, call `Tree.apply()` to sort the object's shape keys according to the tree.
    `Tree.apply()` will **not** automatically call `core.utils.hide()` or `core.utils.show()`.
    """
    
    active = None # type: Tree
    
    def __init__(self):
        self.tree = []
        self.cache = {}
        
        if bpy.context.object and bpy.context.object.data.shape_keys:
            self.tree = self._tree(bpy.context.object.data.shape_keys.key_blocks)
        
        self.forget()
    
    def __str__(self):
        import json
        return json.dumps(self.tree, indent=4, default=repr)
    
    def _tree(self, keys):
        branch = []
        
        stop = len(keys)
        
        i = 0
        
        while i < stop:
            key = keys[i]
            children = core.folder.get_children(key)
            
            if core.key.is_folder(key):
                branch.append([key.name] + list(itertools.chain(self._tree(children))))
            else:
                branch.append(key.name)
            
            i += 1 + len(children)
        
        return branch
    
    def forget(self):
        self.cache = {
            'flattened': [],
            'ancestries': {},
            'parents': {},
            'families': {},
            'locations': {}
        }
    
    def get_flattened(self):
        if self.cache['flattened']:
            return self.cache['flattened']
        
        self.cache['flattened'] = core.utils.flatten(self.tree)
        return self.cache['flattened']
    
    def get_ancestry(self, name):
        if name in self.cache['ancestries']:
            return self.cache['ancestries'][name]
        
        self.cache['ancestries'][name] = self.ancestry(name)
        return self.cache['ancestries'][name]
    
    def get_parents(self, name):
        if name in self.cache['parents']:
            return self.cache['parents'][name]
        
        self.cache['parents'][name] = [p[0] for p in self.get_ancestry(name)[1:][::-1]]
        return self.cache['parents'][name]
    
    def get_family(self, name):
        if name in self.cache['families']:
            return self.cache['families'][name]
        
        ans = self.get_ancestry(name)
        fam = ans[-1][1:] if len(ans) > 1 else ans[-1]
        
        self.cache['families'][name] = fam
        return self.cache['families'][name]
    
    def get_location(self, name):
        if name in self.cache['locations']:
            return self.cache['locations'][name]
        
        self.cache['locations'][name] = self.locate(name)
        return self.cache['locations'][name]
    
    def index(self, name):
        return self.get_flattened().index(name)
    
    def locate(self, name, root=None):
        assert type(name) == str
        
        root = root or self.tree
        
        for i, branch in enumerate(root):
            if type(branch) == list:
                loc = self.locate(name, branch)
                
                if loc:
                    if name in loc[0] and loc[0].index(name) == 0:
                        return (root, i)
                    
                    return loc
            
            elif branch == name:
                return (root, i)
    
    def move(self, name, mode):
        ans = self.ancestry(name)
        loc = self.locate(name, ans[-1])
        
        if mode == 'TOP':
            loc[0].insert(len(ans) > 1 or loc[1] > 1, loc[0].pop(loc[1]))
        elif mode == 'UP':
            loc[0].insert(core.utils.loop(loc[1] - 1, len(ans) > 1, len(loc[0])), loc[0].pop(loc[1]))
        elif mode == 'DOWN':
            loc[0].insert(core.utils.loop(loc[1] + 1, 1, len(loc[0])), loc[0].pop(loc[1]))
        elif mode == 'BOTTOM':
            loc[0].append(loc[0].pop(loc[1]))
        
        self.forget()
    
    def reinsert(self, a, b=None):
        if a == b:
            return
        
        ansa = self.ancestry(a)
        ansb = self.ancestry(b) if b else None
        loca = self.locate(a, ansa[-1])
        locb = self.locate(b, ansb[-1]) if b else None
        
        if b:
            locb[0].insert(locb[1] - (loca[0] == locb[0] and loca[1] < locb[1]), loca[0].pop(loca[1]))
        else:
            self.tree.append(loca[0].pop(loca[1]))
        
        self.forget()
    
    def transfer(self, a, b):
        if a == b:
            return
        
        ansa = self.ancestry(a)
        ansb = self.ancestry(b)
        loca = self.locate(a, ansa[-1])
        locb = self.locate(b, ansb[-1])
        
        if b:
            locb[0][locb[1]].append(loca[0].pop(loca[1]))
        
        self.forget()
    
    def ancestry(self, name):
        stop = self.index(name)
        ancestry = [self.tree]
        
        i = 0
        j = 0
        
        while j <= stop:
            branch = ancestry[-1][i]
            
            if type(branch) == list:
                size = len(core.utils.flatten(branch))
                
                if j + size > stop:
                    ancestry.append(branch)
                    i = 0
                else:
                    i += 1
                    j += size
            else:
                i += 1
                j += 1
        
        if i == 1 and len(ancestry) > 1:
            return ancestry[:-1]
        else:
            return ancestry
    
    def get(self, name):
        return core.utils.get(*self.locate(name))
    
    def apply(self):
        """Sorts the object's shape keys according to this Tree."""
        
        obj = bpy.context.object
        key_blocks = obj.data.shape_keys.key_blocks
        
        for destination, name in enumerate(core.utils.flatten(self.tree)):
            index = key_blocks.find(name)
            
            while index != destination:
                obj.active_shape_key_index = index
                bpy.ops.object.shape_key_move(type='UP' if destination < index else 'DOWN')
                
                index += (-1 if destination < index else 1)
            
            if core.key.is_folder(key_blocks[name]):
                core.folder.set_block_value(key_blocks[name], 'children', len(self.get(name)) - 1)


tree = Tree
frame = {}


def changed():
    _frame = {
        'object': bpy.context.object,
        'comparator': []
    }
    
    if _frame['object'] and _frame['object'].data.shape_keys:
        for i, key in enumerate(_frame['object'].data.shape_keys.key_blocks):
            _frame['comparator'].append({
                'hash': hash(key),
                'name': key.name,
                'index': i,
                'children': core.folder.get_capacity(key, recursive=False)
            })
    
    global frame
    
    _changed = _frame != frame
    
    if _changed:
        frame = _frame
        Tree.active = Tree()
    
    return _changed
