#!/usr/bin/env python3
import re
import os
import argparse
import sys
from typing import List
import platform

VALID_DOT_IMAGE_FORMATS = ["png", "jpg", "svg"]
GRAPHVIZ_BLOCK_START = "```graphviz\n"
CONTENT_BLOCK = ".+?"
BLOCK_END = "\n```"

SCRIPT_PATH: str = os.path.dirname(os.path.realpath(__file__))

def get_graphviz_blocks(markdown_text: str) -> List[str]:
    MARKDOWN_BLOCK_RE = f"{GRAPHVIZ_BLOCK_START}{CONTENT_BLOCK}{BLOCK_END}"
    return re.findall(MARKDOWN_BLOCK_RE, markdown_text, re.DOTALL)

def find_content_in_block(block: str) -> str:
    CONTENT_PATTERN = f"{GRAPHVIZ_BLOCK_START}(?P<content>{CONTENT_BLOCK}){BLOCK_END}"
    return re.search(CONTENT_PATTERN, block, re.DOTALL).group("content")

def write_dot(block: str, path: str, image_name_without_extension: str) -> None:
    content: str = find_content_in_block(block)
    dot_output_file = os.path.join(path, image_name_without_extension + ".dot")
    print(f"Wrote dot to {dot_output_file}")
    with open(dot_output_file, "w") as f:
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

def create_html(path: str, filename: str, use_css: bool) -> None:
    output_filename = \
        os.path.join(path, "out", os.path.splitext(file_name)[0] + "_out.html")
    css_arg = "--css pandoc.css" if use_css else ""
    os.system(f"pandoc --standalone {css_arg} --output={output_filename} {filename}")
    os.system(f'echo "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />" >> {output_filename}')
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
    print(f"Running command {command}")
    os.system(command)
    return image_file_path

def get_output_markdown_text_and_write_images(
        markdown_text: str, graphviz_blocks: List[str], path: str, fmt: str) \
        -> str:
    print(f"Found {len(graphviz_blocks)} graphviz blocks")
    for block_index, block in enumerate(graphviz_blocks):
        print(f"Found block of size {len(block)}")
        name_without_extension: str = f"graphviz_image_{block_index}"
        write_dot(block, path, name_without_extension)
        write_image_from_dot_file(path, name_without_extension, fmt=fmt)
        image_path_in_markdown = f"./images/{name_without_extension}.{fmt}"
        image_link: str = f"![image]({image_path_in_markdown})"

        markdown_text = markdown_text.replace(block, image_link)

    return markdown_text

def ensure_directory_exists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

def replace_graphviz_with_images(path: str, file_name: str, fmt: str) -> str:
    """
    Opens file specified by path + file_name, then writes
    * A new markdown file where all graphviz blocks are replaced.
    * One image for every graphviz block found in the markdown file
    """
    with open(os.path.join(path, file_name)) as f:
        markdown_text: str = f.read()
    graphviz_blocks: List[str] = get_graphviz_blocks(markdown_text)

    if not graphviz_blocks:
        print("No graphviz blocks found!")
        exit()

    images_path = os.path.join(path, "out", "images")
    ensure_directory_exists(images_path)

    output_markdown_text = \
        get_output_markdown_text_and_write_images(
            markdown_text, graphviz_blocks, images_path, fmt=fmt)

    output_filename = \
        os.path.join(path, "out", os.path.splitext(file_name)[0] + "_out.md")
    with open(output_filename, "w") as f:
        f.write(output_markdown_text)
    print(f"Wrote output file to {output_filename}")
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

    output_filename = replace_graphviz_with_images(path, file_name, fmt)

    if args.output_pdf:
        create_pdf(path, filename=output_filename)
    elif args.output_html:
        create_html(path, filename=output_filename, use_css=True)
