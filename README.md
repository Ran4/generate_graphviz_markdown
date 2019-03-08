Hack to generate markdown with links to rendered images from a markdown document
containing inline graphviz and/or plantuml code blocks.

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

Assuming we have a file `path/to/file.md`:


    Example document.

    ```graphviz
    digraph "Wonderful graphviz graph" {
        label="\G"
        a -> b;
        b -> c;
    }
    ```
    
    ```plantuml
    alice -> bob : Request
    bob -> bob : Authorize
    bob -> alice : Response
    ```

    End of document.

Then this will generate a file `path/to/out/file_out.html`:

```
python3 generate_graphviz_images.py --output-html path/to/file.md
```
