#!/usr/bin/env python

# tcviz 1.2
#
# Licensed under the terms of the MIT/X11 license.
# Copyright (c) 2009-2013 Vita Smid <http://ze.phyr.us>


from __future__ import absolute_import
import subprocess
import sys
from itertools import chain

from Filter import Filter
from Node import Node
from io import open

TCPATH = u'/sbin/tc'


def main():
    f = u''
    if len(sys.argv) == 2:
        (q, c) = [readTc([type, u'show', u'dev', sys.argv[1]]) for type in (u'qdisc', u'class')]
    elif len(sys.argv) == 4:
        (q, c, f) = [readFile(p) for p in sys.argv[1:4]]
    else:
        usage()
        return 1

    qdiscs = parse(q, Node)
    classes = parse(c, Node)

    if len(sys.argv) == 2:
        f = u'\n'.join([readTc([u'filter', u'show', u'dev', sys.argv[1], u'parent', unicode(cur._id)]).replace(u'filter', u'filter parent {}'.format(cur._id)) for cur in chain(qdiscs, classes)])

    filters = parse(f, Filter)

    nodes = qdiscs + classes
    gv = u'digraph tc { %s \n %s \n %s \n %s }' % (genSetup(), genNodes(nodes), genEdges(nodes), genEdges(filters))
    print gv
    return 0


def usage():
    print >>sys.stderr, u'Usage: %s <interface>' % sys.argv[0]
    print >>sys.stderr, u'\nOR'
    print >>sys.stderr, u'If you want to feed tcviz with offline data:'
    print >>sys.stderr, u'%s <qdiscs file> <classes file> <filters file>' % sys.argv[0]


def readFile(path):
    return open(path).read()


def readTc(args):
    return subprocess.Popen([TCPATH] + args, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]


def parse(string, constructor):
    specs = []
    for line in string.split(u'\n'):
        if not line:
            continue
        elif line.startswith(u' ') or line.startswith(u'\t'):  # continuation of the previous line
            specs[-1] += u' ' + line.strip()
        else:
            specs.append(line.strip())
    return [constructor(spec) for spec in specs]


def genSetup():
    return u'node [ fontname = "DejaVu Sans" ]; edge [ fontname = "DejaVu Sans" ];'


def genNodes(objects):
    return u'\n'.join([o.getNodeSpec() for o in objects])


def genEdges(objects):
    return u'\n'.join([o.getEdgeSpec() for o in objects])


if __name__ == u'__main__':
    sys.exit(main())
