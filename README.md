Description
-----------
*dir-indexer* is simple index of directory generator written in Python. The
result is HTML file with the content of directory.

Installation
-----------
Just *clone* the repository and run *dir_indexer.py* with proper arguments.

Usage
-----
### Help
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

### Templates
*.html* template should contain some keywords which will be substitued
(none of them is required):
* $index - table with the content of directory
* $gen_date - when the index was created
* $rel\_dir - relative to the initial directory path will be substitued
