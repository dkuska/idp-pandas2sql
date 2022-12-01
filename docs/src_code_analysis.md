# Python Source Code Analysis

There are a number of different approaches when systematically analyzing python source code

1. Tokenizing
    - Implemented through `tokenize` module. [Link](https://docs.python.org/3/library/tokenize.html)
    - Lexical scanning
    - Lowest level possible --> Too finely grained for our purposes
2. AST
    - Abstract syntax tree
    - Available through `ast` mode [Link](https://docs.python.org/3/library/ast.html#)
    - Generates Tree structure with nodes representing actually executable code
    - Removed Whitespaces/Empty Lines/Comments from Tree --> Parsing a src file into an AST and back to code, all this will be lost --> Bad User experience
    - Tree can be traversed/ 'walked' with `NodeVisitors` and `NodeTransformers`
    - Visitors and Transformers have `visit_XY` methods for each type of node that can be overridden
    - Visitor can extract Metadata, which can then be made available to the Transformer in order to transform only certain nodes
3. CST
   - Concrete Syntax Tree
   - Deprecated implementation [RedBaron](https://github.com/PyCQA/redbaron) --> Last update 09/2021
   - Newer implementation [libcst](https://github.com/Instagram/LibCST), [docs](https://libcst.readthedocs.io/en/latest/index.html) created and maintained by Instagram
   - Wrapper around `tokenize` and `ast` which preserves everything that is lost when just using `ast`
   - Mostly intended to be used to create linters and refactoring applications
   - In addition to `Visitors` and `Transformers`, offers special `Provider` Interface which scrapes levels of metadata
   - More intuitive interface than AST
