"""
 File: ecmb_builder_resize_base.py
 Copyright (c) 2023 Clemens K. (https://github.com/metacreature)
 
 MIT License
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""

import io
from PIL import Image
from abc import ABC, abstractmethod


class ecmbBuilderResizeBase(ABC):

    _target_width = None
    _target_height = None
    _webp_compression = None
    _compress_all = None

    def __init__(self, target_width: int, target_height: int, webp_compression: int, compress_all: bool) -> None:
        self._target_width = target_width
        self._target_height = target_height
        self._webp_compression = webp_compression
        self._compress_all = compress_all


    def process(self, fp_full: str|io.BytesIO) -> list[str|io.BytesIO]:
        pillow_full = Image.open(fp_full)
        width, height = pillow_full.size

        if (width / height) > (self._target_width / self._target_height * 1.5):
            pillow_full, resized = self._resize(pillow_full, self._target_width * 2, self._target_height)
        else:
            pillow_full, resized = self._resize(pillow_full, self._target_width, self._target_height)

        if resized or self._compress_all:
            fp_full = io.BytesIO()
            pillow_full.save(fp_full, 'webp', quality = self._webp_compression, method=5)

        return self._split_image(fp_full, pillow_full)
    


    def _split_image(self, fp_full: str|io.BytesIO, pillow_full: Image) -> list[str|io.BytesIO]:
        width, height = pillow_full.size
        
        if (width / height) < (self._target_width / self._target_height * 1.5):
            if type(fp_full) == str:
                pillow_full.close()
            return [fp_full]
            
        pillow_left = pillow_full.crop((0, 0, round(width/2), height))
        fp_left = io.BytesIO()
        pillow_left.save(fp_left, 'webp', quality = self._webp_compression, method=5)
        del pillow_left
        
        pillow_right = pillow_full.crop((round(width/2), 0, width, height))
        fp_right = io.BytesIO()
        pillow_right.save(fp_right, 'webp', quality = self._webp_compression, method=5)
        del pillow_right
        
        if type(fp_full) == str:
            pillow_full.close()

        return [fp_full, fp_left, fp_right]
    

    @abstractmethod
    def _resize(self, pillow_full: Image, target_width: int, target_height: int) -> [io.BytesIO, Image]:
        pass