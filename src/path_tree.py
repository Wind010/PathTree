from typing import Any, Dict, List, Set, Union

class PathTree:
    '''
    A tree structure composed of nested dictionaries to all for quick storage and lookup of a blob path.
    '''

    def __init__(self):
        self.root: Union[Dict[Any, Any], Set[str]] = {}
        self.__prev_path_parts = ''
        self.__leaf_parent: Union[Dict[Any, Any]] = {}


    def add(self, parts: List, sep: str = '/') -> 'PathTree':
        '''
        Populate the root dictionary.
        Time Complexity: O(n) where n is the number of items in parts/path.
        Space Complexity: O(n)
        '''

        if isinstance(parts, str):
            parts = parts.split(sep)
        
        if len(parts) == 0:
            return self

        if len(parts) == 1:
            if parts[0] != '':
                self.root = set([parts[0]])
                return self
            else:
                return self
        
        # If the parent of the leaf node exists we just append to leaf node.
        # The O(n-1) time complexity of join is added.
        leaf_parent_dir_path, leaf_parent_dir_name, blob_name = '/'.join(parts[:-1]), parts[-2], parts[-1]

        if self.__prev_path_parts == leaf_parent_dir_path and leaf_parent_dir_name in self.__leaf_parent:
             self.__leaf_parent[leaf_parent_dir_name].add(blob_name)
             return self

        self.__prev_path_parts = leaf_parent_dir_path # O(n-1) cost on this join.
        self.root.update(self._populate(parts, self.root)) # type: ignore
        return self


    def _populate(self, parts: List[str], tree: Dict, parent: str=None) \
            -> Union[Dict[str, Union[Dict[Any, Any], Set[str]]], Set[str]]:
        if not parts:
            return tree

        first_part: str = parts[0]
        rest_of_parts: List[str] = parts[1:]

        if first_part == '':
            return tree

        if len(parts) == 1 and parent:
            return {first_part}

        if first_part not in tree:
            child_node = self._populate(rest_of_parts, tree, first_part)
            node_set = {parts[0]: child_node}
            if len(rest_of_parts) == 1:
                self.__leaf_parent = node_set
            return node_set  # type: ignore
        else:
            node:Union[Dict[str, Union[Dict[Any, Any], Set[str]]], Set[str]] \
                = self._populate(rest_of_parts, tree[first_part], first_part)
            tree[first_part] = tree[first_part] | node
        return tree


    def contains(self, path: Union[List[str], str], sep: str='/') -> bool:
        '''
        Searches given path within root of tree.
        Time Complexity: O(n) where n is the number of parts/path.
        Space Complexity: O(1)
        - TODO:  Consider how to handle path with no filename.  If dir_path matches, return True?  Allow wildcard?
        '''
        parts = path
        if isinstance(path, str):
            parts = path.split(sep)
        else:
            parts = path

        def search(tree, parts):
            for part in parts:
                if part in tree:
                    if isinstance(tree, Set):
                        return True
                    return search(tree[part], parts[1:])
            return False

        return search(self.root, parts)


    def get_flat_list(self, root = None, sep = '/'):
        '''
        List all paths in tree with separator.
        Time Complexity: O(n + 1) where n is the number of nodes in the tree and lookup of blob name
        from the leaf node which is a set.
        Space Complexity: O(1)
        '''

        if not root:
            root = self.root

        def flatten(tree):
            def expand(key, value):
                if not isinstance(value, set):
                    return [(key + sep + k, v) for k, v in flatten(value).items()]
                else:
                    return [(key, value)]

            items = [item for k, v in tree.items() for item in expand(k, v)]
            return dict(items)
        
        return [path + sep + leaf for path, leaves in flatten(root).items() for leaf in leaves]

    
    def __iter__(self):
        ''' Returns the Iterator object '''
        return iter(self.get_flat_list(self.root))
        