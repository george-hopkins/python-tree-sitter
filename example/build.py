from treesitter.build import language_builder

builder = language_builder('_treesitter_language', 'tree_sitter_python', '../vendor/tree-sitter-python')

if __name__ == '__main__':
    builder.compile(verbose=True)
