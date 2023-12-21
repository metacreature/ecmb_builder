from PIL import Image
from math import ceil
from .ecmb_builder_resize_base import ecmbBuilderResizeBase

class ecmbBuilderResizeMax(ecmbBuilderResizeBase):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> [Image, bool]:
        orig_width, orig_height = pillow_orig.size
        if orig_width <= final_width and orig_height <= final_height:
            return (pillow_orig, False)


        if (final_width / final_height) < (orig_width / orig_height):
            target_width = final_width
            target_height = ceil(final_width * (orig_height / orig_width))

            if target_height > final_height:
                target_height = final_height

        else:
            target_width = ceil(final_height * (orig_width / orig_height))
            target_height = final_height

            if target_width > final_width:
                target_width = final_width

        
        pillow_resized = pillow_orig.resize((target_width, target_height))
        

        return (pillow_resized, True)