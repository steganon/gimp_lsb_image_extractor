#!/usr/bin/env python

# 1. Place this file in the GIMP plug-ins folder and restart GIMP
# 2. Open an steganon artwork which has an embedded hidden image
# 3. Click menu item Filters->steganon->Decode Hidden Image
# 3. Wait a minute and see the extracted image
#
# Author: steganon

import math
from gimpfu import *
from array import array

def python_lsb_image_extractor(img, srclayer):

    try:
        pdb.gimp_message("Extracting hidden image...")
        pdb.gimp_image_undo_group_start(img)

        pdb.gimp_progress_init("Extracting hidden image...", None)
        layer = srclayer.copy()
        img.add_layer(layer, 0)
        pdb.gimp_item_set_name(layer, "extracted")
        width = layer.width
        height = layer.height

        rgn = layer.get_pixel_rgn(0, 0, width, height, TRUE, FALSE)
        src_pixels = array("B", rgn[0:width, 0:height])

        p_size = len(rgn[0,0])
	
        for y in range(height):
            for x in range(width):
                src_pos = (x + width * y) * p_size
                pixel = src_pixels[src_pos: src_pos + p_size]
                # Hidden in the green channel
                pixel[0] = pixel[2] = pixel[1] = 255 if pixel[1]&1 else 0
                src_pixels[src_pos: src_pos + p_size] = pixel
            pdb.gimp_progress_update(y/float(height))

        rgn[0:width, 0:height] = src_pixels.tostring()

        layer.flush()
        layer.update(0,0,width,height)
        pdb.gimp_image_undo_group_end(img)
        pdb.gimp_progress_end()
        pdb.gimp_message("Finished!")

    except Exception, err:
        pdb.gimp_message("ERR: " + str(err))
        pdb.gimp_image_undo_group_end(img)

register(
        "python_lsb_image_extractor",
        "Extract an image hidden using LSB steganography",
        "Extract an image hidden using LSB steganography",
        "steganon",
        "steganon",
        "2023",
        "<Image>/Filters/steganon/Extract Hidden Image",
        "RGB*",
        [],
        [],
        python_lsb_image_extractor)

main()
