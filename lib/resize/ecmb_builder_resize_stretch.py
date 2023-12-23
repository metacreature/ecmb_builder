from PIL import Image
from .ecmb_builder_resize_base import ecmbBuilderResizeBase

class ecmbBuilderResizeStretch(ecmbBuilderResizeBase):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> [Image, bool]:
        orig_width, orig_height = pillow_orig.size

        if orig_width == final_width and orig_height == final_height:
            return (pillow_orig, False)

        pillow_resized = pillow_orig.resize((final_width, final_height))
        
        pillow_orig.close()
        del pillow_orig

        return (pillow_resized, True)