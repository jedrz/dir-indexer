#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import time
import datetime
import sys
import argparse
import string


DATE_FORMAT = '%d-%m-%Y %H:%M'

TABLE_START = '<table>'

TABLE_HEADING = '''    <tr>
        <th>Name</th>
        <th>Modified</th>
        <th>Size</th>
    </tr>'''

TABLE_DIR = '''    <tr>
        <td class="name"><a href="{esc_name}/index.html">{name}</a></td>
        <td class="modified">{modified}</td>
        <td class="size"></td>
    </tr>'''

TABLE_FILE = '''    <tr>
        <td class="name"><a href="{esc_name}">{name}</a></td>
        <td class="modified">{modified}</td>
        <td class="size">{size}</td>
    </tr>'''

TABLE_END = '</table>'


def format_size(size_b):
    """Format size given in bytes"""
    units = ('B', 'KB', 'MB', 'GB')
    size = float(size_b)
    for unit in units:
        if size <= 2048 or unit == units[-1]:
            return '{:.2f} {}'.format(size, unit)
        size /= 1024


def format_mtime(mtime):
    """Format time given in seconds"""
    mtime = time.localtime(mtime)
    return time.strftime(DATE_FORMAT, mtime)


def is_excluded(path, excluded_paths, excluded_names, show_hidden=False):
    """Check if 'path' is excluded in some way.

    arguments:
    path -- path to check
    excluded_paths -- paths which are compared with 'path' as the same files
    excluded_names -- basename of 'path' is compared with them
    show_hidden -- show hidden files (starting with '.')
    """
    for ex in excluded_paths:
        try:
            if os.path.samefile(path, ex):
                return True
        except OSError:
            pass
    if os.path.basename(path) in excluded_names:
        return True
    if not show_hidden and os.path.basename(path).startswith('.'):
        return True
    return False


def escape_characters(s):
    """Espace spaces as %20"""
    return s.replace(' ', '%20')


def create_index(root, dirnames, filenames, template, excluded_paths=[],
                 excluded_names=[], show_hidden=False, rel_dir=''):
    """Create the index for 'root' directory. Simply a table with
    the content of 'root' is inserted into template.

    The index is saved in root/index.html.
    Existing index.html will be overwritten.

    arguments:
    root -- path to directory which should be indexed
    dirnames -- names of directories in 'root'
    filenames -- files in 'root'
    template -- string.Template instance with:
                $index - table with the content of 'root' will be placed here
                $gen_date - generation date
                $rel_dir - path from initial directory
    excluded_paths -- paths which should be excluded from indexing
    excluded_names -- {file,dir}names which should be excluded from indexing
    show_hidden -- show hidden files (starting with '.')
    rel_dir -- initial directory - 'root'
    """
    # build table
    table = [TABLE_START, TABLE_HEADING]
    # is_excluded shortut for use of filter function
    is_excluded_short = \
        lambda path: not is_excluded(path, excluded_paths, excluded_names,
                                     show_hidden)
    for d in sorted(
            filter(is_excluded_short, dirnames),
            key=str.lower):
        table.append(TABLE_DIR.format(
            esc_name=escape_characters(d),
            name=d,
            modified=format_mtime(os.path.getmtime(os.path.join(root, d)))))
    for f in sorted(
            filter(is_excluded_short, filenames),
            key=str.lower):
        table.append(TABLE_FILE.format(
            esc_name=escape_characters(f),
            name=f,
            modified=format_mtime(os.path.getmtime(os.path.join(root, f))),
            size=format_size(os.path.getsize(os.path.join(root, f)))))
    table.append(TABLE_END)

    gen_date = datetime.datetime.now().strftime(DATE_FORMAT)

    with open(os.path.join(root, 'index.html'), 'w') as index_file:
        # fill the template
        index_file.write(template.safe_substitute(index='\n'.join(table),
                                                  gen_date=gen_date,
                                                  rel_dir=rel_dir))


def get_rel_dir(path, root):
    """Return path - root.

    example:
    path = '/home/user/sth1/sth2/sth3/sth4'
    root = '/home/user/sth1/sth2'
    result: /sth3/sth4
    """
    path = os.path.normpath(path)
    root = os.path.normpath(root)
    if len(path) == len(root):
        return '/'
    else:
        return path[len(root):]


def walk_level(path, level=-1):
    """Similar to os.walk function but with yielding current level
    from 'path'.
    Argument 'level' -- how deep the recusion will go (if less than 0 then
    there is no limit).

    from: http://stackoverflow.com/a/234329
    """
    num_sep = path.count(os.sep)
    for root, dirnames, filenames in os.walk(path):
        cur_level = root.count(os.sep) - num_sep
        yield root, dirnames, filenames, cur_level
        if level >= 0 and cur_level >= level:
            # it omits directories under some level
            # you can read about this trick in python docs
            del dirnames[:]


def generate(path, template_path, quiet=False, recursive=False, level=0,
             excluded_paths=[], excluded_names=[], show_hidden=False):
    """Create the index for 'path' and optionally deeper with a template.

    arguments:
    path -- where the indexing should start
    template_path -- path to html template
    quiet -- will print some information or no
    recursive -- should directiory in 'path' be indexed recursively,
                 if 'recursive' is True then 'level' is ignored
    level -- set the maximum level of recursion ('recursive' must be False
             to 'level' has the effect)
    excluded_paths -- paths which should be excluded from indexing
    excluded_names -- {file,dir}names which should be excluded from indexing
    show_hidden -- show hidden files (starting with '.')
    """
    with open(template_path) as template_source:
        template = string.Template(template_source.read())
    # hide index.html
    excluded_names += ['index.html']
    for root, dirnames, filenames, cur_level in walk_level(
            path, -1 if recursive else level):
        # check if current directory is the last to be indexed
        # then hide dirnames
        if not recursive and level <= cur_level:
            dirnames = []
        create_index(root, dirnames, filenames, template,
                     excluded_paths, excluded_names, show_hidden,
                     get_rel_dir(root, path))
        if not quiet:
            print('Directory {} indexed'.format(root))


def main():
    parser = argparse.ArgumentParser(
        description='Generate a html file with the content of directory',
        epilog='All index.html files will be OVERWRITTEN')
    parser.add_argument('path',
                        help='path to index')
    parser.add_argument('-t', '--template',
                        help='path to HTML template file',
                        default='templates/default.html')
    parser.add_argument('-q', '--quiet',
                        help='print nothing',
                        action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-R', '-r', '--recursive',
                        help='generate pages recursively',
                        action='store_true')
    group.add_argument('-l', '--level',
                        help='generate pages recursively with the maximum '
                             'recursion depth level',
                        type=int, default=0)
    parser.add_argument('-e', '--exclude',
                        help='exclude path(s) from being indexed',
                        nargs='+', default=[], metavar='PATH')
    parser.add_argument('--exclude-names',
                        help='exclude name(s) from being indexed '
                             '(basenames are being compared)',
                        nargs='+', default=[], metavar='NAME')
    parser.add_argument('--hidden',
                        help='show hidden files',
                        action='store_true')
    args = parser.parse_args()

    # check paths given by the user
    if not os.path.isdir(args.path):
        print('{} is not a directory'.format(args.path))
        sys.exit(1)
    if not (os.path.isfile(args.template)):
        print('Given template path {} is not a file'.format(args.template))
        sys.exit(1)

    generate(args.path, args.template, args.quiet, args.recursive, args.level,
             args.exclude, args.exclude_names, args.hidden)


if __name__ == '__main__':
    main()
