Hack to generate markdown with links to rendered images from a markdown document
containing graphviz and/or plantuml blocks.

This *should* probably be done as pandoc filters.

## Dependencies

Python >= 3.6, due to usage of f-strings.

#### External dependencies

* For html and pdf output: Pandoc https://pandoc.org/
* For graphviz blocks: Graphviz dot (the "dot" CLI program) https://www.graphviz.org/
* For plantuml blocks: The node-plantuml CLI: https://www.npmjs.com/package/node-plantuml (the "puml" CLI program)
"""

## Usage

```sh
python3 generate_graphviz_images.py --help
```

#### Example

```
python3 generate_graphviz_images.py --output-html path/to/file.md
```
