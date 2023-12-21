from PIL import Image
from math import ceil
from .ecmb_builder_resize_base import ecmbBuilderResizeBase

class ecmbBuilderResizeCover(ecmbBuilderResizeBase):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> [Image, bool]:
        orig_width, orig_height = pillow_orig.size

        if orig_width == final_width and orig_height == final_height:
            return (pillow_orig, False)

        offset_x = 0
        offset_y = 0

        if (final_width / final_height) > (orig_width / orig_height):
            target_width = final_width
            target_height = ceil(final_width * (orig_height / orig_width))

            if (final_height - target_height) != 0:
                offset_y = ceil((target_height - final_height) / 2)
        else:
            target_width = ceil(final_height * (orig_width / orig_height))
            target_height = final_height

            if (final_width - target_width) != 0:
                offset_x = ceil((target_width - final_width) / 2)
        
        if offset_x or offset_y:
            pillow_tmp = pillow_orig.resize((target_width, target_height))
            pillow_resized = pillow_tmp.crop((offset_x, offset_y, offset_x + final_width, offset_y + final_height))    
        else:
            pillow_resized = pillow_orig.resize((final_width, final_height))
        

        return (pillow_resized, True)