##############################################################################
# Copyright (c) 2013, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Written by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://scalability-llnl.github.io/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License (as published by
# the Free Software Foundation) version 2.1 dated February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
"""\
The ``compilation`` module contains utility functions used by the compiler
wrapper script.

.. todo::

   Think about moving this into the script to increase compilation
   speed.

"""
import os
import sys


def get_env_var(name, required=True):
    value = os.environ.get(name)
    if required and value is None:
        print "%s must be run from spack." % os.path.abspath(sys.argv[0])
        sys.exit(1)
    return value


def get_env_flag(name, required=False):
    value = get_env_var(name, required)
    if value:
        return value.lower() == "true"
    return False


def get_path(name):
    path = os.environ.get(name, "").strip()
    if path:
        return path.split(":")
    else:
        return []


def parse_rpaths(arguments):
    """argparse, for all its features, cannot understand most compilers'
       rpath arguments.  This handles '-Wl,', '-Xlinker', and '-R'"""
    def get_next(arg, args):
        """Get an expected next value of an iterator, or die if it's not there"""
        try:
            return next(args)
        except StopIteration:
            # quietly ignore -rpath and -Xlinker without args.
            return None

    other_args = []
    def linker_args():
        """This generator function allows us to parse the linker args separately
           from the compiler args, so that we can handle them more naturally.
        """
        args = iter(arguments)
        for arg in args:
            if arg.startswith('-Wl,'):
                sub_args = [sub for sub in arg.replace('-Wl,', '', 1).split(',')]
                for arg in sub_args:
                    yield arg
            elif arg == '-Xlinker':
                target = get_next(arg, args)
                if target is not None:
                    yield target
            else:
                other_args.append(arg)

    # Extract all the possible ways rpath can appear in linker args, then
    # append non-rpaths to other_args.  This happens in-line as the linker
    # args are extracted, so we preserve the original order of arguments.
    # This is important for args like --whole-archive, --no-whole-archive,
    # and others that tell the linker how to handle the next few libraries
    # it encounters on the command line.
    rpaths = []
    largs = linker_args()
    for arg in largs:
        if arg == '-rpath':
            target = get_next(arg, largs)
            if target is not None:
                rpaths.append(target)

        elif arg.startswith('-R'):
            target = arg.replace('-R', '', 1)
            if not target:
                target = get_next(arg, largs)
                if target is None: break

            if os.path.isdir(target):
                rpaths.append(target)
            else:
                other_args.extend(['-Wl,' + arg, '-Wl,' + target])
        else:
            other_args.append('-Wl,' + arg)
    return rpaths, other_args
