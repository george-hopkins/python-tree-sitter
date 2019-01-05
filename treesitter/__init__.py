import os.path
import io
from cffi import FFI
from ._bindings import ffi, lib


class Parser():
    def __init__(self):
        self._parser = ffi.gc(lib.ts_parser_new(), lib.ts_parser_delete)

    def set_language(self, language):
        lib.ts_parser_set_language(self._parser, language)

    def parse(self, bytes_or_file):
        if isinstance(bytes_or_file, io.IOBase):
            bytes_or_file = bytes_or_file.read()
        if not isinstance(bytes_or_file, bytes):
            raise TypeError(type(bytes_or_file))
        tree = lib.ts_parser_parse_string(self._parser, ffi.NULL, bytes_or_file, len(bytes_or_file))
        if tree == ffi.NULL:
            raise RuntimeError('Could not parse string')
        return Tree(ffi.gc(tree, lib.ts_tree_delete))


class Tree():
    def __init__(self, tree):
        self._tree = tree

    def root(self):
        return Node(self._tree, lib.ts_tree_root_node(self._tree))

    def copy(self):
        tree = ffi.gc(lib.ts_tree_copy(self._tree), lib.ts_tree_delete)
        return Tree(tree)


class Node():
    def __init__(self, tree, node):
        self._tree = tree
        self._node = node

    def type(self):
        type = lib.ts_node_type(self._node)
        if type == ffi.NULL:
            return None
        return ffi.string(type).decode()

    def start_byte(self):
        return lib.ts_node_start_byte(self._node)

    def end_byte(self):
        return lib.ts_node_end_byte(self._node)

    def start_point(self):
        point = lib.ts_node_start_point(self._node)
        return (point.row, point.column)

    def end_point(self):
        point = lib.ts_node_end_point(self._node)
        return (point.row, point.column)

    def bytes(self, source):
        return source[self.start_byte():self.end_byte()]

    def children(self):
        return Children(self)

    def named_children(self):
        return NamedChildren(self)

    def sexp(self):
        sexp = lib.ts_node_string(self._node)
        sexp_str = ffi.string(sexp).decode()
        lib.free(sexp)
        return sexp_str


class Children():
    def __init__(self, node):
        self._node = node
        self._count = lib.ts_node_child_count(node._node)

    def __len__(self):
        return self._count

    def __getitem__(self, index):
        if index < 0:
            index = self._count + index
        if not (0 <= index < self._count):
            raise IndexError()
        return Node(self._node._tree, lib.ts_node_child(self._node._node, index))


class NamedChildren():
    def __init__(self, node):
        self._node = node
        self._count = lib.ts_node_named_child_count(node._node)

    def __len__(self):
        return self._count

    def __getitem__(self, index):
        if index < 0:
            index = self._count + index
        if not (0 <= index < self._count):
            raise IndexError()
        return Node(self._node._tree, lib.ts_node_named_child(self._node._node, index))
