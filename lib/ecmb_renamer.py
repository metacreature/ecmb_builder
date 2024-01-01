"""
 File: ecmb_builder.py
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

import re, os, path, hashlib
from datetime import datetime
from .ecmb_builder_base import ecmbBuilderBase
from .ecmblib.src.ecmblib import ecmbException


class ecmbRenamer(ecmbBuilderBase):
    
    def rename(self) -> None:
        
        if self._book_config.is_initialized:
            raise ecmbException('Book is allready initialized!')
        
        (chapter_folders, volume_folders) = self._read_folder_structure()

        self._rename_path(chapter_folders, 'chapter_', 4)
        if volume_folders:
            self._rename_path(volume_folders, 'volume_', 3)

        (chapter_folders, volume_folders) = self._read_folder_structure()

        image_nr = 0
        for folder in chapter_folders:
            file_list = self._get_image_list(folder['path'] + folder['name'])
            image_nr = self._rename_path(file_list, 'img_', 6, '0', image_nr)


    def _rename_path(self, path_list: list, prefix:str, zfill: int, suffix:str = '', start_at: int = 0) -> int:
        tmp_name = '__ecmbbuilder_tmpname_' + hashlib.md5(str(datetime.now()).encode()).hexdigest() + '_'

        try:
            cnt = start_at
            for item in path_list:
                cnt += 1
                new_name = item['name'] + tmp_name + (str(cnt).zfill(zfill))
                new_name += '.' + item.get('extension') if item.get('extension') else ''
                os.rename(item['path'] + item['name'], item['path'] + new_name)
                item['tmp_name'] = new_name

            cnt = start_at
            for item in path_list:
                cnt += 1
                new_name = prefix + (str(cnt).zfill(zfill)) + suffix
                new_name += '.' + item.get('extension') if item.get('extension') else ''
                os.rename(item['path'] + item['tmp_name'], item['path'] + new_name)
        except PermissionError:
            try:
                for item in path_list:
                    if item.get('tmp_name'):
                        os.rename(item['path'] + item['tmp_name'], item['path'] + item['name'])
            except:
                pass
            
            raise ecmbException('Permission denied for rename folders/images. Please close opened files and folders!')

        return start_at + cnt


        
    



        
