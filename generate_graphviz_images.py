#!/usr/bin/env python3
"""
External dependencies:
* For html and pdf output: Pandoc
* For graphviz blocks: Graphviz dot (the "dot" CLI program)
* For plantuml blocks: The node-plantuml CLI: https://www.npmjs.com/package/node-plantuml (the "puml" CLI program)
"""
from typing import List, Dict
import argparse
import os
import platform
import re
import sys
import warnings

VALID_DOT_IMAGE_FORMATS = ["png", "jpg", "svg"]
GRAPHVIZ_BLOCK_START = "```graphviz\n"
PUML_BLOCK_START = "```plantuml\n"
CONTENT_BLOCK = ".+?"
BLOCK_END = "\n```"

VALID_PUML_IMAGE_FORMATS = ["png", "svg"]

SCRIPT_PATH: str = os.path.dirname(os.path.realpath(__file__))

def get_graphviz_blocks(markdown_text: str) -> List[str]:
    MARKDOWN_BLOCK_RE = f"{GRAPHVIZ_BLOCK_START}{CONTENT_BLOCK}{BLOCK_END}"
    return re.findall(MARKDOWN_BLOCK_RE, markdown_text, re.DOTALL)

def get_plantuml_blocks(markdown_text: str) -> List[str]:
    # TODO: Implement this
    MARKDOWN_BLOCK_RE = f"{PUML_BLOCK_START}{CONTENT_BLOCK}{BLOCK_END}"
    return re.findall(MARKDOWN_BLOCK_RE, markdown_text, re.DOTALL)

def get_blocks(markdown_text: str) -> Dict[str, List[str]]:
    # TODO: Use this function
    return {
        "graphviz": get_graphviz_blocks(markdown_text),
        "plantuml": get_plantuml_blocks(markdown_text),
    }

def find_content_in_block(block: str) -> str:
    if block.startswith(GRAPHVIZ_BLOCK_START):
        block_start = GRAPHVIZ_BLOCK_START
    elif block.startswith(PUML_BLOCK_START):
        block_start = PUML_BLOCK_START
    else:
        raise Exception("Unknown start of block", block)
    CONTENT_PATTERN = f"{block_start}(?P<content>{CONTENT_BLOCK}){BLOCK_END}"
    return re.search(CONTENT_PATTERN, block, re.DOTALL).group("content")

def write_text_file(block: str, path: str, image_name: str) -> None:
    content: str = find_content_in_block(block)
    text_output_file = os.path.join(path, image_name)
    print(f"        Wrote text file to {text_output_file}")
    with open(text_output_file, "w") as f:
        f.write(content)

def copy_css_file(path: str) -> None:
    pandoc_css_path = os.path.join(SCRIPT_PATH, "pandoc.css")
    output_css_path: str = os.path.join(path, "out", "pandoc.css")
    print(f"Copying over pandoc.css to {output_css_path}")
    os.system(f"cp {pandoc_css_path} {output_css_path}")

def create_pdf(path: str, filename: str) -> None:
    output_filename = \
        os.path.join(path, "out", os.path.splitext(file_name)[0] + "_out.pdf")
    os.system(f"pandoc --css pandoc.css --standalone --output={output_filename} {filename}")
    copy_css_file(path=path)

def add_content_type_meta_to_file(filename: str) -> None:
    with open(filename, "a") as f:
        f.write('<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />')

def create_html(path: str, filename: str, use_css: bool) -> None:
    output_filename = \
        os.path.join(path, "out", os.path.splitext(file_name)[0] + "_out.html")
    css_arg = "--css pandoc.css" if use_css else ""
    os.system(f"pandoc --standalone {css_arg} --output={output_filename} {filename}")
    add_content_type_meta_to_file(output_filename)
    if use_css:
        copy_css_file(path=path)

def write_image_from_dot_file(path: str,
                              image_name_without_extension: str,
                              fmt: str) \
                              -> str:
    assert fmt in VALID_DOT_IMAGE_FORMATS
    if platform.system() == "Windows":
        DOT_COMMAND = "dot.exe"
    else:
        DOT_COMMAND = "dot"
    dot_file_path = os.path.join(path, image_name_without_extension + ".dot")
    image_file_path = os.path.join(path, image_name_without_extension + "." + fmt)
    command = f"{DOT_COMMAND} -T{fmt} {dot_file_path} > {image_file_path}"
    print(f"        Running command {command}")
    os.system(command)
    return image_file_path

def write_image_from_plantuml_file(path: str,
                                   image_name_without_extension: str,
                                   fmt: str) \
                                   -> str:
    assert fmt in VALID_PUML_IMAGE_FORMATS
    puml_file_path = os.path.join(path, image_name_without_extension + ".plantuml")
    image_file_path = os.path.join(path, image_name_without_extension + "." + fmt)
    if fmt.lower() == "png":
        FMT_ARG = "--png"
    elif fmt.lower() == "svg":
        FMT_ARG = "--svg"
    else:
        raise Exception(f"Unhandled plantuml image format {fmt}")
    command = f"puml generate {FMT_ARG} {puml_file_path} -o {image_file_path}"
    print(f"        Running command {command}")
    os.system(command)
    return image_file_path

def get_output_markdown_text_and_write_graphviz_images(
        markdown_text: str, graphviz_blocks: List[str], path: str, fmt: str) \
        -> str:
    print(f"\nFound {len(graphviz_blocks)} graphviz blocks")
    for block_index, block in enumerate(graphviz_blocks):
        print(f"    * Graphviz block {block_index+1} of {len(graphviz_blocks)}")
        name_without_extension: str = f"graphviz_image_{block_index}"
        write_text_file(block, path, name_without_extension + ".dot")
        write_image_from_dot_file(path, name_without_extension, fmt=fmt)
        image_path_in_markdown = f"./images/{name_without_extension}.{fmt}"
        image_link: str = f"![]({image_path_in_markdown})"

        markdown_text = markdown_text.replace(block, image_link)

    return markdown_text

def get_output_markdown_text_and_write_puml_images(
        markdown_text: str, puml_blocks: List[str], path: str, fmt: str) \
        -> str:
    print(f"\nFound {len(puml_blocks)} plantUML blocks")
    for block_index, block in enumerate(puml_blocks):
        print(f"    * Plantuml block {block_index+1} of {len(puml_blocks)}")
        name_without_extension: str = f"plantuml_image_{block_index}"
        write_text_file(block, path, name_without_extension + ".plantuml")
        write_image_from_plantuml_file(path, name_without_extension, fmt=fmt)
        image_path_in_markdown = f"./images/{name_without_extension}.{fmt}"
        image_link: str = f"![]({image_path_in_markdown})"

        markdown_text = markdown_text.replace(block, image_link)

    return markdown_text

def ensure_directory_exists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

def replace_md_blocks_with_images(path: str, file_name: str, fmt: str) -> str:
    """
    Opens file specified by path + file_name, then writes
    * A new markdown file where all graphviz+plantuml blocks are replaced.
    * One image for every graphviz and plantuml block found in the markdown file
    """
    with open(os.path.join(path, file_name)) as f:
        markdown_text: str = f.read()
    blocks: Dict[str, List[str]] = get_blocks(markdown_text)
    graphviz_blocks: List[str] = blocks["graphviz"]
    plantuml_blocks: List[str] = blocks["plantuml"]

    if not graphviz_blocks and not plantuml_blocks:
        print("No graphviz or plantuml blocks found!")
        exit()

    images_path = os.path.join(path, "out", "images")
    ensure_directory_exists(images_path)

    markdown_text = \
        get_output_markdown_text_and_write_graphviz_images(
            markdown_text, graphviz_blocks, images_path, fmt=fmt)

    markdown_text = \
        get_output_markdown_text_and_write_puml_images(
            markdown_text, plantuml_blocks, images_path, fmt=fmt)

    output_filename = \
        os.path.join(path, "out", os.path.splitext(file_name)[0] + "_out.md")
    with open(output_filename, "w") as f:
        f.write(markdown_text)
    print(f"\nWrote output file to {output_filename}")
    return output_filename

def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a markdown document with dot images from a"
                    "markdown document with inlined graphviz blocks")
    parser.add_argument("markdown_filepath")
    parser.add_argument(
        "-T", "--image-format", default="svg", choices=VALID_DOT_IMAGE_FORMATS)
    parser.add_argument(
        "--output-pdf",
        action="store_true",
        default=False,
        help="If set, also generate pdf from output md using pandoc")
    parser.add_argument(
        "--output-html",
        action="store_true",
        default=False,
        help="If set, also generate html from output md using pandoc")
    return parser

if __name__ == "__main__":
    args = get_arg_parser().parse_args()

    full_path: str = args.markdown_filepath
    path, file_name = os.path.dirname(full_path), os.path.basename(full_path)
    fmt: str = args.image_format

    output_filename = replace_md_blocks_with_images(path, file_name, fmt)

    if args.output_pdf:
        create_pdf(path, filename=output_filename)
    elif args.output_html:
        create_html(path, filename=output_filename, use_css=True)
