from PIL import Image, ImageEnhance, ImageOps
from math import ceil
from .ecmb_builder_resize_max import ecmbBuilderResizeMax

class ecmbBuilderResizeCropmax(ecmbBuilderResizeMax):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> [Image, bool]:
        orig_width, orig_height = pillow_orig.size
        
        pillow_tmp = ImageEnhance.Contrast(pillow_orig.convert('RGB')).enhance(5)
        pillow_tmp = ImageOps.invert(pillow_tmp)
        
        box = pillow_tmp.getbbox()
        box_width = box[2] - box[0]

        if not (box_width < orig_width * 0.99 and box_width > orig_width * 0.85):
            return super()._resize(pillow_orig, final_width, final_height)

        pillow_resized = pillow_orig.crop((box[0], 0, box[2], orig_height))

        if orig_width <= final_width and orig_height <= final_height:
            return (pillow_resized, True)
        else:
            return super()._resize(pillow_resized, final_width, final_height)