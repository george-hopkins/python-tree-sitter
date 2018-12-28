import treesitter
from _treesitter_language.lib import tree_sitter_python

CODE = b'''
def example(a, b):
    return a + b
'''

parser = treesitter.Parser()
parser.set_language(tree_sitter_python())

tree = parser.parse(CODE)
root = tree.root()
for node in root.named_children():
    print(node.sexp())
