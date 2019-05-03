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

Assuming we have a file `some_path/file.md`:


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

Then this command:

```
python3 generate_graphviz_images.py --output-html path/to/file.md
```

will generate a file `some_path/out/file_out.html` and associated images, like this:

```
.
├ file.md
└ out
    ├ file_out.html
    ├ file_out.md
    ├ images
    │   ├ graphviz_image_0.dot
    │   ├ graphviz_image_0.svg
    │   ├ plantuml_image_0.plantuml
    │   └ plantuml_image_0.svg
    └ pandoc.css
```
