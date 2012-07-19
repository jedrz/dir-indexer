#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import time
import datetime
import sys
import argparse


DATE_FORMAT = '%d-%m-%Y %H:%M'


def format_size(size_b):
    if size_b <= 1024:
        return '{:.2f} b'.format(size_b)
    size_kb = size_b / 1024
    if size_kb <= 1024:
        return '{:.2f} kb'.format(size_kb)
    size_mb = size_kb / 1024
    if size_mb <= 1024:
        return '{:.2f} mb'.format(size_mb)
    size_gb = size_mb / 1024
    return '{:.2f} gb'.format(size_gb)


def format_mtime(mtime):
    """Format time given in seconds"""
    mtime = time.localtime(mtime)
    return time.strftime(DATE_FORMAT, mtime)


def is_excluded(path, excluded_paths, excluded_names, show_hidden=False):
    """Check if path should be excluded from indexing"""
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


def create_index(root, dirnames, filenames, template, excluded_paths=[],
                 excluded_names=[], show_hidden=False):
    """Create an index for 'root' directory.
    The index is saved in root/index.html.

    arguments:
     root -- path to directory which should be indexed
     dirnames -- names of directories in 'root'
     filenames -- files in 'root'
     template -- html template
    """
    table = ['''<table>
        <tr>
            <th>Name</th>
            <th>Modified</th>
            <th>Size</th>
        </tr>''']
    for d in dirnames:
        if not is_excluded(os.path.join(root, d), excluded_paths,
                           excluded_names, show_hidden):
            statinfo = os.stat(os.path.join(root, d))
            table.append('''<tr>
                    <td class="name"><a href="{}">{}</a></td>
                    <td class="modified">{}</td>
                    <td></td>
                </tr>'''.format(os.path.join(d, 'index.html'), d,
                                format_mtime(statinfo.st_mtime)))
    for f in filenames:
        if not is_excluded(os.path.join(root, f), excluded_paths,
                           excluded_names, show_hidden):
            statinfo = os.stat(os.path.join(root, f))
            table.append('''<tr>
                    <td class="name"><a href="{0}">{0}</a></td>
                    <td class="modified">{1}</td>
                    <td class="size">{2}</td>
                </tr>'''.format(f, format_mtime(statinfo.st_mtime),
                                   format_size(statinfo.st_size)))
    table.append('</table>')

    gen_date = datetime.datetime.now()
    gen_date = gen_date.strftime(DATE_FORMAT)

    with open(os.path.join(root, 'index.html'), 'w') as outfile:
        outfile.write(template.format(files='\n'.join(table),
                                      gen_date=gen_date))


def walk_level(path, level=1):
    """os.walk function but with recursion depth level"""
    num_sep = path.count(os.sep)
    for root, dirnames, filenames in os.walk(path):
        yield root, dirnames, filenames
        cur_num_sep = root.count(os.sep)
        if cur_num_sep + 1 >= num_sep + level:
            # it omits directories under some level
            # you can read about this trick in python docs
            del dirnames[:]


def generate(path, template_dir, quiet=False, recursive=False, level=1,
             excluded_paths=[], excluded_names=[], show_hidden=False):
    template_path = os.path.join(template_dir, 'index.html')
    css_path = os.path.join(template_dir, 'styles.css')
    with open(template_path) as template:
        template = template.read()
    # hide index.html and styles.css
    excluded_names += ['index.html', 'styles.css']

    mywalk = lambda p: os.walk(p) if recursive else lambda p: \
            walk_level(p, level)
    for root, dirnames, filenames in mywalk(path):
        if recursive or level > 1:
            create_index(root, dirnames, filenames, template,
                         excluded_paths, excluded_names)
        else:
            create_index(root, [], filenames, template,
                         excluded_paths, excluded_names)
        shutil.copy(css_path, root)
        if not quiet:
            print('Created index.html and styles.css in {}'.format(root))


def main():
    parser = argparse.ArgumentParser(
            description='Generate a html file with the content of directory',
            epilog='All index.html and styles.css files will be OVERWRITTEN'
    )
    parser.add_argument('path',
                        help='path to public folder')
    parser.add_argument('-t', '--template',
                        help='used template',
                        default='templates/default')
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
                        type=int, default=1)
    parser.add_argument('-e', '--exclude',
                        help='exclude path(s) from being indexed',
                        nargs='+', default=[], metavar='PATH')
    parser.add_argument('--exclude-names',
                        help='exclude names from being indexed '
                             '(basenames are being compared)',
                        default=[], metavar='NAME')
    parser.add_argument('--hidden',
                        help='show hidden files',
                        action='store_true')
    args = parser.parse_args()


    if not os.path.isdir(args.path):
        print('{} is not a directory'.format(args.path))
        sys.exit(1)
    if not (os.path.isfile(os.path.join(args.template, 'index.html')) and
            os.path.isfile(os.path.join(args.template, 'styles.css'))):
        print('Given template path {} is invalid'.format(args.template))
        sys.exit(1)

    generate(args.path, args.template, args.quiet, args.recursive, args.level,
             args.exclude, args.exclude_names, args.hidden)


if __name__ == '__main__':
    main()
