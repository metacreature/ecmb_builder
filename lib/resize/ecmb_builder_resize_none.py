from PIL import Image
from .ecmb_builder_resize_base import ecmbBuilderResizeBase

class ecmbBuilderResizeNone(ecmbBuilderResizeBase):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> [Image, bool]:
        return (pillow_orig, False)

