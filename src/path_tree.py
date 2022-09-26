from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

class PathTree:
    """
    A tree structure composed of nested dictionaries to all for quick storage and lookup of a blob path.
    """

    def __init__(self):
        self.root: Union[Dict[Any, Any], Set[str]] = {}
        self.__prev_path_parts = ''
        self.__leaf_parent: Dict[Any, Any] = {}


    def add(self, parts: Union[List[str], str], sep: str = '/') -> 'PathTree':
        """
        Populate the root dictionary.
        Time Complexity: O(n) where n is the number of items in parts/path.
        Space Complexity: O(n)
        """

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

        child = self._populate(parts, self.root)
        if isinstance(self.root, set) and isinstance(child, dict):
            self.root = child
        else:
            self.root.update(child) # type: ignore
            
        return self


    def _populate(self, parts: List[str] 
            , tree: Any
            , parent: Optional[str]=None) \
            -> Union[Dict[str, Union[Dict[Any, Any], Set[str], Dict[str, Set[str]]]], Set[str]]:
        """
        Populate/build the PathTree
        :parts: Parts of the path split by delim (/).
        :tree: Is either a dictionary of dictionaries or dictionary of sets or a set.
               Will be a set if we're at the end of the path (leaf), otherwise will be a dictionary 
               mirroring the file path with key being the current directory and key it's child(ren).
        """
        if not parts:
            return tree

        first_part: str = parts[0]
        rest_of_parts: List[str] = parts[1:]

        if first_part == '':
            return tree

        if len(parts) == 1 and parent:
            return {first_part}

        if first_part in tree:
            level = tree if isinstance(tree, set) else tree[first_part]
            child: Union[Dict[Any, Any], Set[str]] = self._populate(rest_of_parts, level, first_part)

            tree = self._populate_set_with_set(first_part, tree, child)
            tree = self._populate_set_with_dict(first_part, tree, child) 
            tree = self._populate_dict_with_set(first_part, tree, child)
            tree = self._populate_dict_with_dict(first_part, rest_of_parts, tree, child)

        else:
            child_node = self._populate(rest_of_parts, tree, first_part)
            dict_node = {parts[0]: child_node}
            if len(rest_of_parts) == 1:
                self.__leaf_parent = dict_node
            return dict_node  # type: ignore

        return tree


    def _populate_set_with_set(self, first_part: str, parent: Set[str], child: Union[Dict[Any, Any], Set[str]] ) \
        -> Union[Dict[Any, Any], Set[str]]:
        """Both parent and child are sets."""
        if isinstance(parent, Dict) or isinstance(child, Dict):
            return parent

        if first_part in parent:
            return {first_part: child}
        else:
            # Both A and B are sets and siblings so update/add to set.
            parent |= child

        return parent


    def _populate_set_with_dict(self, first_part: str, parent: Set[str], child: Union[Dict[Any, Any], Set[str]] ) \
        -> Union[Dict[Any, Any], Set[str]]:
        """Parent is set and child is dictionary"""
        if isinstance(parent, Dict) or isinstance(child, Set):
            return parent

        # A is set and B is dictionary 
        return {first_part: child}


    def _populate_dict_with_set(self, first_part: str, parent: Dict[Any, Any], child: Union[Dict[Any, Any], Set[str]]) \
        -> Union[Dict[Any, Any], Set[str]]:
        """Parent is dictionary and child is set"""
        if isinstance(parent, Set) or isinstance(child, Dict):
            return parent

        # Case when A is dictionary and B is set.
        for c in child:
            if c in parent[first_part]:
                continue
            
            self._populate_set_with_set(first_part, parent[first_part], child)
        return parent


    def _populate_dict_with_dict(self, first_part: str, rest_of_parts: List[str]
        , parent: Dict[Any, Any], child: Union[Dict[Any, Any], Set[str]] ) -> Union[Dict[Any, Any], Set[str]]:
        """Parent is dictionary and child is dictionary"""
        if isinstance(parent, Set) or isinstance(child, Set):
            return parent

        if first_part in parent:
            key = rest_of_parts[0]
            if key in parent[first_part] and key in child:
                # Merge on same level.
                parent[first_part] = child
            elif first_part == key:
                # We create a new object and with this which is not the same as |= or .update().
                parent[first_part] = parent[first_part] | child
            else:
                parent[first_part] |= child
        else:
            # Both A and B are dictionary.
            parent[first_part] = child

        return parent


    def contains(self, path: Union[List[str], str], sep: str='/') -> bool:
        """
        Searches given path within root of tree.
        Time Complexity: O(n) where n is the number of parts/path.
        Space Complexity: O(1)
        """
        parts = path
        if isinstance(path, str):
            parts = path.split(sep)
        else:
            parts = path

        def search(tree, parts):
            if isinstance(tree, Set):
                return set(parts).issubset(tree)

            for part in parts:
                if part in tree:
                    t = tree if isinstance(tree, set) else tree[part]
                    # Return true here instead of another level of recursion to ensure parts not empty.
                    return search(t, parts[1:]) if parts[1:] else True  
                return False
            return True
        return search(self.root, parts)


    def get_flat_list(self, root = None, sep = '/'):
        """
        List all paths in tree with separator.  Note that this will not yield the exact paths passed in
        since only the full paths are stored and no duplication of paths.  Will not return sub-paths.
        Time Complexity: O(n + 1) where n is the number of nodes in the tree and lookup of blob name
        from the leaf node which is a set.
        Space Complexity: O(1)
        """

        if not root:
            root = self.root

        def flatten(tree) -> List[Tuple[str, set]]:
            def expand(key, value):
                if not value:
                    return [(key, value)]
                if isinstance(value, dict):
                    return [(key + sep + k, v) if v else (key, {k}) for k, v in flatten(value) ]
                if isinstance(value, set):
                    return [(key, {val}) for val in value]
                return []

            return [item for k, v in tree.items() for item in expand(k, v)]
        
        return [path + sep + leaf if leaves else path 
            for path, leaves in flatten(root) for leaf in leaves]


    
    def __iter__(self):
        """ Returns the Iterator object """
        if isinstance(self.root, dict):
            return iter(self.get_flat_list(self.root))
        return iter(self.root)
        