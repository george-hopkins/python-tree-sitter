import ast
from pathlib import Path
from cffi import FFI


def _load_gyp(contents):
    tree = ast.parse(contents)
    assert isinstance(tree, ast.Module)
    return _load_gyp_node(tree.body[0].value)


def _load_gyp_node(node):
    if isinstance(node, ast.Dict):
        dict = {}
        for key, value in zip(node.keys, node.values):
            assert isinstance(key, ast.Str)
            key = key.s
            dict[key] = _load_gyp_node(value)
        return dict
    elif isinstance(node, ast.List):
        children = []
        for child in node.elts:
            children.append(_load_gyp_node(child))
        return children
    elif isinstance(node, ast.Str):
        return node.s
    else:
        raise TypeError()


def _runtime_root():
    return Path(__file__).parent.parent / 'vendor' / 'tree-sitter'


def _gyp_target(path, target):
    gyp = _load_gyp(path.open().read())
    try:
        return next(t for t in gyp['targets'] if t['target_name'] == target)
    except StopIteration:
        raise RuntimeError('Could not find target: ' + target)


def language_builder(package, function, dir):
    runtime_root = _runtime_root()
    runtime_gyp = _gyp_target(runtime_root / 'project.gyp', 'runtime')
    language_root = Path(dir).resolve()
    language_gyp = _gyp_target(language_root / 'binding.gyp', function + '_binding')

    sources = [str(language_root / f) for f in language_gyp['sources'] if f != 'src/binding.cc']
    include_dirs = [str(runtime_root / d) for d in runtime_gyp['include_dirs']]
    include_dirs.extend([str(language_root / d) for d in language_gyp['include_dirs']])

    builder = FFI()
    builder.include(runtime_builder())
    builder.cdef('const TSLanguage *{}(void);'.format(function))
    builder.set_source(package, '''
#include <tree_sitter/runtime.h>
#include <tree_sitter/parser.h>
const TSLanguage *{}(void);
'''.format(function),
        sources=sources,
        include_dirs=include_dirs)

    return builder


def runtime_builder():
    root = _runtime_root()
    gyp_target = _gyp_target(root / 'project.gyp', 'runtime')

    builder = FFI()
    builder.cdef(r'''
    typedef uint16_t TSSymbol;
    typedef struct TSLanguage TSLanguage;
    typedef struct TSParser TSParser;
    typedef struct TSTree TSTree;

    typedef enum {
        TSInputEncodingUTF8,
        TSInputEncodingUTF16,
    } TSInputEncoding;

    typedef enum {
        TSSymbolTypeRegular,
        TSSymbolTypeAnonymous,
        TSSymbolTypeAuxiliary,
    } TSSymbolType;

    typedef struct {
        uint32_t row;
        uint32_t column;
    } TSPoint;

    typedef struct {
        TSPoint start_point;
        TSPoint end_point;
        uint32_t start_byte;
        uint32_t end_byte;
    } TSRange;

    typedef struct {
        void *payload;
        const char *(*read)(void *payload, uint32_t byte_index, TSPoint position, uint32_t *bytes_read);
        TSInputEncoding encoding;
    } TSInput;

    typedef enum {
        TSLogTypeParse,
        TSLogTypeLex,
    } TSLogType;

    typedef struct {
        void *payload;
        void (*log)(void *payload, TSLogType, const char *);
    } TSLogger;

    typedef struct {
        uint32_t start_byte;
        uint32_t old_end_byte;
        uint32_t new_end_byte;
        TSPoint start_point;
        TSPoint old_end_point;
        TSPoint new_end_point;
    } TSInputEdit;

    typedef struct {
        uint32_t context[4];
        const void *id;
        const TSTree *tree;
    } TSNode;

    typedef struct {
        const void *tree;
        const void *id;
        uint32_t context[2];
    } TSTreeCursor;

    TSParser *ts_parser_new(void);
    void ts_parser_delete(TSParser *);
    const TSLanguage *ts_parser_language(const TSParser *);
    bool ts_parser_set_language(TSParser *, const TSLanguage *);
    TSLogger ts_parser_logger(const TSParser *);
    void ts_parser_set_logger(TSParser *, TSLogger);
    void ts_parser_print_dot_graphs(TSParser *, FILE *);
    void ts_parser_halt_on_error(TSParser *, bool);
    TSTree *ts_parser_parse(TSParser *, const TSTree *, TSInput);
    TSTree *ts_parser_parse_string(TSParser *, const TSTree *, const char *, uint32_t);
    TSTree *ts_parser_parse_string_encoding(TSParser *, const TSTree *, const char *, uint32_t, TSInputEncoding);
    bool ts_parser_enabled(const TSParser *);
    void ts_parser_set_enabled(TSParser *, bool);
    size_t ts_parser_operation_limit(const TSParser *);
    void ts_parser_set_operation_limit(TSParser *, size_t);
    void ts_parser_reset(TSParser *);
    void ts_parser_set_included_ranges(TSParser *, const TSRange *, uint32_t);
    const TSRange *ts_parser_included_ranges(const TSParser *, uint32_t *);

    TSTree *ts_tree_copy(const TSTree *);
    void ts_tree_delete(TSTree *);
    TSNode ts_tree_root_node(const TSTree *);
    void ts_tree_edit(TSTree *, const TSInputEdit *);
    TSRange *ts_tree_get_changed_ranges(const TSTree *, const TSTree *, uint32_t *);
    void ts_tree_print_dot_graph(const TSTree *, FILE *);
    const TSLanguage *ts_tree_language(const TSTree *);

    uint32_t ts_node_start_byte(TSNode);
    TSPoint ts_node_start_point(TSNode);
    uint32_t ts_node_end_byte(TSNode);
    TSPoint ts_node_end_point(TSNode);
    TSSymbol ts_node_symbol(TSNode);
    const char *ts_node_type(TSNode);
    char *ts_node_string(TSNode);
    bool ts_node_eq(TSNode, TSNode);
    bool ts_node_is_null(TSNode);
    bool ts_node_is_named(TSNode);
    bool ts_node_is_missing(TSNode);
    bool ts_node_has_changes(TSNode);
    bool ts_node_has_error(TSNode);
    TSNode ts_node_parent(TSNode);
    TSNode ts_node_child(TSNode, uint32_t);
    TSNode ts_node_named_child(TSNode, uint32_t);
    uint32_t ts_node_child_count(TSNode);
    uint32_t ts_node_named_child_count(TSNode);
    TSNode ts_node_next_sibling(TSNode);
    TSNode ts_node_next_named_sibling(TSNode);
    TSNode ts_node_prev_sibling(TSNode);
    TSNode ts_node_prev_named_sibling(TSNode);
    TSNode ts_node_first_child_for_byte(TSNode, uint32_t);
    TSNode ts_node_first_named_child_for_byte(TSNode, uint32_t);
    TSNode ts_node_descendant_for_byte_range(TSNode, uint32_t, uint32_t);
    TSNode ts_node_named_descendant_for_byte_range(TSNode, uint32_t, uint32_t);
    TSNode ts_node_descendant_for_point_range(TSNode, TSPoint, TSPoint);
    TSNode ts_node_named_descendant_for_point_range(TSNode, TSPoint, TSPoint);
    void ts_node_edit(TSNode *, const TSInputEdit *);

    TSTreeCursor ts_tree_cursor_new(TSNode);
    void ts_tree_cursor_delete(TSTreeCursor *);
    void ts_tree_cursor_reset(TSTreeCursor *, TSNode);
    TSNode ts_tree_cursor_current_node(const TSTreeCursor *);
    bool ts_tree_cursor_goto_parent(TSTreeCursor *);
    bool ts_tree_cursor_goto_next_sibling(TSTreeCursor *);
    bool ts_tree_cursor_goto_first_child(TSTreeCursor *);
    int64_t ts_tree_cursor_goto_first_child_for_byte(TSTreeCursor *, uint32_t);

    uint32_t ts_language_symbol_count(const TSLanguage *);
    const char *ts_language_symbol_name(const TSLanguage *, TSSymbol);
    TSSymbol ts_language_symbol_for_name(const TSLanguage *, const char *);
    TSSymbolType ts_language_symbol_type(const TSLanguage *, TSSymbol);
    uint32_t ts_language_version(const TSLanguage *);

    void free(void *ptr);
    ''')
    builder.set_source('treesitter._bindings', '#include <tree_sitter/runtime.h>',
        include_dirs=[str(root / s) for s in gyp_target['include_dirs']],
        sources=[str(root / s) for s in gyp_target['sources']])

    return builder


if __name__ == "__main__":
    runtime_builder().compile(verbose=True)
