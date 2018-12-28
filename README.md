# python-tree-sitter

Python bindings for [tree-sitter](https://tree-sitter.github.io/tree-sitter)


## Getting Started

```python
import treesitter
from _your_language.lib import tree_sitter_yourlanguage

parser = treesitter.Parser()
parser.set_language(tree_sitter_yourlanguage())

tree = parser.parse(b'...')
root = tree.root()
for node in root.named_children():
    print(node.sexp())
```

Because language parsers are usually implemented in C, we need to compile them first. Take a look at [`example/`](./example/) to see a full setup.
