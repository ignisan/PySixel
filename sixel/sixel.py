#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012  Hayaki Saito <user@zuse.jp>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****

import sys,os
from converter import SixelConverter

class SixelWriter:
    
    def __init__(self, f8bit = False):
        self.f8bit = f8bit
        if f8bit: # 8bit mode
            self.CSI='\x9b'
        else:
            self.CSI='\x1b['

    def save_position(self):
        sys.stdout.write('\x1b7')

    def restore_position(self):
        sys.stdout.write('\x1b8')

    def move_x(self, n, fabsolute):
        sys.stdout.write(self.CSI)
        if fabsolute:
            sys.stdout.write('%d`' % n)
        elif n > 0:
            sys.stdout.write('%dC' % n)
        elif n < 0:
            sys.stdout.write('%dD' % -n)

    def move_y(self, n, fabsolute):
        sys.stdout.write(self.CSI)
        if fabsolute:
            sys.stdout.write('%dd' % n)
        elif n > 0:
            sys.stdout.write('%dB' % n)
        elif n < 0:
            sys.stdout.write('%dA' % n)

    def draw(self,
             filename,
             absolute=False,
             x=None,
             y=None,
             w=None,
             h=None,
             alphathreshold=0,
             chromakey=False):

        self.save_position()

        try:
            if not x is None:
                self.move_x(x, absolute)

            if not y is None:
                self.move_y(y, absolute)

            sixel_converter = SixelConverter(filename,
                                             self.f8bit,
                                             w,
                                             h,
                                             alphathreshold=alphathreshold,
                                             chromakey=chromakey)

            output = sixel_converter.getvalue()
            env = os.environ
            if env.has_key("TERM") and "screen" in env["TERM"]:
                # (ST+DCS) splits sixel terminator, because ST(sixel's terminator)
                # is identified as ST(screen's terminator)
                # (ST+DCS) is equivalent to NOP in this context.
                n = 512-8
                DCS,ST="\x1bP","\x1b\\"
                ST2 = "\x1b"+(ST+DCS)+"\\"
                output = output.replace("\x90", DCS
                              ).replace("\x9c", ST2
                              ).replace("\x1b\\", ST2)
                for chunk in [output[i:i+n] for i in range(0,len(output),n)]:
                    sys.stdout.write(DCS)
                    sys.stdout.write(chunk)
                    sys.stdout.write(ST)
                    sys.stdout.flush()
            else:
                sys.stdout.write(output)

        finally:
            self.restore_position()
        

