#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import time
import sys
import argparse


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
    mtime = time.localtime(mtime)
    return time.strftime('%d.%m.%y %H:%M', mtime)


def create_html(root, dirs, files, template):
    with open(os.path.join(root, 'index.html'), 'w') as outfile:
        table = ['''<table>
        <tr>
            <th>Name</th>
            <th>Modified</th>
            <th>Size</th>
        </tr>
        ''']
        for d in dirs:
            table.append('''<tr>
                    <td class="name"><a href="{}">{}</a></td>
                </tr>'''.format(os.path.join(d, 'index.html'), d)) 
        for f in files:
            statinfo = os.stat(os.path.join(root, f))
            table.append('''<tr>
                    <td class="name"><a href="{0}">{0}</a></td>
                    <td class="modified">{1}</td>
                    <td class="size">{2}</td>
                </tr>'''.format(f, format_mtime(statinfo.st_mtime),
                                   format_size(statinfo.st_size)))
        table += ['</table>']
        outfile.write(template.format(files='\n'.join(table)))


def generate(path, template_dir):
    template_path = os.path.join(template_dir, 'index.html')
    css_path = os.path.join(template_dir, 'styles.css')
    with open(template_path) as template:
        template = template.read()

    for root, dirs, files in os.walk(path):
        create_html(root, dirs, files, template)
        shutil.copy(css_path, root)


def main():
    parser = argparse.ArgumentParser(description='Generate')
    parser.add_argument('path',
                        help='path to public folder')
    parser.add_argument('-v', '--verbose',
                        help='increase more verbose output',
                        action='store_true')
    parser.add_argument('-t', '--template',
                        help='used template',
                        default='templates/default')
    parser.add_argument('-R', '-r', '--recursive',
                        help='generate pages recursively',
                        action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print('{} is not a directory'.format(args.path))
        sys.exit(1)
    if not (os.path.isfile(os.path.join(args.template, 'index.html')) and
            os.path.isfile(os.path.join(args.template, 'styles.css'))):
        print('Given template path {} is invalid'.format(args.template))
        sys.exit(1)

    generate(args.path, args.template)


if __name__ == '__main__':
    main()
