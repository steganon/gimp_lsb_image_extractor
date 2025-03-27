#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gegl
import sys
from array import array

plug_in_proc   = "plug-in-steganon-lsb-extractor"
plug_in_binary = "steganon-lsb-extractor"

def lsb_extractor_run(procedure, run_mode, image, drawables, config, data):
  parent   = drawables[0].get_parent ()
  position = image.get_item_position (drawables[0])
  try:
        print("Extracting hidden image...")
        Gimp.message("Extracting hidden image...")
        image.undo_group_start()

        Gimp.progress_init("Extracting hidden image...")
        layer = drawables[0].copy()
        width = layer.get_width()
        height = layer.get_height()
        
        layer.set_name("extracted")
        image.insert_layer(layer, parent, position)

        buffer = layer.get_buffer()
        rect = Gegl.Rectangle.new(0,0,width, height)
        src_pixels = buffer.get(
                rect,
                1.0,
                None,
                Gegl.AbyssPolicy(0)
                )

        out_pixels = array('B', src_pixels)
        p_size = int(len(src_pixels)/float(width*height))
        for y in range(height):
            for x in range(width):
                src_pos = (x + width * y) * p_size
                pixel = out_pixels[src_pos: src_pos + p_size]
                # Hidden in the green channel
                pixel[0] = pixel[2] = pixel[1] = 255 if pixel[1]&1 else 0
                out_pixels[src_pos: src_pos + p_size] = pixel
            Gimp.progress_update(y/float(height))

        buffer.set(
                rect,
                'RGBA u8',
                out_pixels,
                )

        buffer.flush()

        layer.update(0,0,width,height)
        Gimp.progress_end()
        Gimp.message("Finished!")

  except Exception as err:
        Gimp.message("ERR: " + str(err))
        print("ERR: " + str(err))
  image.undo_group_end()
  return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


class SteganonLsbExtractor (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc ]

  def do_create_procedure(self, name):
    procedure = None

    if name == plug_in_proc:
      procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          lsb_extractor_run, None)
      procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                      Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
      procedure.set_menu_label("_Extract Hidden Image")
      procedure.set_attribution("steganon", "steganon", "2025")
      procedure.add_menu_path ("<Image>/Filters/steganon")
      procedure.set_documentation ("Extract an image hidden using LSB steganography",
                                   "Extract an image hidden using LSB steganography",
                                   None)
      print("do_create_procedure", plug_in_proc)

    return procedure

Gimp.main(SteganonLsbExtractor.__gtype__, sys.argv)
