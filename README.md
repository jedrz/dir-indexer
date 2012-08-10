## Description
*dir-indexer* is a simple index of directory generator written in
Python. The result is an HTML file (`index.html`) with the index of
the directory as a table with links to files and folders within the
directory, size and modification date.


## Installation
Just clone the repository and run `dir_indexer.py` with proper arguments.

### Requirements
This script was tested under Python 2.7 and 3.2.

## Usage
### Help
Help printed using `-h/--help` option.

    usage: dir_indexer.py [-h] [-t TEMPLATE] [-q] [-R | -l LEVEL]
                          [-e PATH [PATH ...]] [--exclude-names NAME [NAME ...]]
                          [--hidden]
                          path

    positional arguments:
      path                  path to index

    optional arguments:
      -h, --help            show this help message and exit
      -t TEMPLATE, --template TEMPLATE
                            path to HTML template file
      -q, --quiet           print nothing
      -R, -r, --recursive   generate pages recursively
      -l LEVEL, --level LEVEL
                            generate pages recursively with the maximum recursion
                            depth level
      -e PATH [PATH ...], --exclude PATH [PATH ...]
                            exclude path(s) from being indexed
      --exclude-names NAME [NAME ...]
                            exclude name(s) from being indexed (basenames are
                            being compared)
      --hidden              show hidden files

#### Example usage
    python dir_indexer.py path/to/folder -r -t templates/default.html
This command will create `index.html` files recursively in every
directory into *folder* with `default.html` file used as a template.

### Templates
*.html* template should contain some keywords which will be substitued
(none of them is required):
* `$index` - table with the content of directory will be placed here
* `$gen_date` - when the index was created
* `$rel_dir` - relative to the initial directory path