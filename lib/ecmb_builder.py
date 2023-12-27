import re, os, path, hashlib
from tqdm import tqdm
from datetime import datetime
from .ecmb_builder_utils import ecmbBuilderUtils
from .ecmb_builder_config import ecmbBuilderConfig
from .ecmb_builder_book_config import ecmbBuilderBookConfig
from .resize.ecmb_builder_resize_base import ecmbBuilderResizeBase
from .ecmblib.ecmb import ecmbBook, ecmbException


class ecmbBuilder():
    
    _builder_config = None
    _book_config = None

    _folder_name = None
    _source_dir = None
    _output_dir = None


    def __init__(self, folder_name:str):
        self._builder_config = ecmbBuilderConfig()
        self._set_dirs(folder_name)
        self._book_config = ecmbBuilderBookConfig(self._builder_config, self._source_dir)


    def initialize(self) -> None:
        if self._book_config.is_initialized:
            raise ecmbException('Book is allready initialized!')
        self._rename_source_files()
        self._init_book_config()

        print('\033[1;32;40m  Open "' + self._source_dir + 'book_config.json" and add all the meta-data to your book!\x1b[0m\n')


    def build(self, volumes: int|list[int]) -> None:
        if not self._book_config.is_initialized:
            raise ecmbException('Book is not initialized! Run "invoke init ' + self._folder_name + '" first!')
        
        resize_method = self._load_resize_method()
        
        if self._book_config.chapter_list:
            self._build_book(resize_method, '', self._book_config.chapter_list)
        else:
            if volumes != None:
                volumes = volumes if type(volumes) == list else [volumes]

            volume_nr = 0
            for volume_dir, chapter_list in self._book_config.volume_list.items():
                volume_nr += 1
                if volumes and volume_nr not in volumes:
                    continue
                self._build_book(resize_method, volume_dir, chapter_list, volume_nr)


    def _build_book(self, resize_method: ecmbBuilderResizeBase, volume_dir: str, chapter_list: list, volume_nr: int = None) -> None:
        config = self._book_config

        file_name = re.sub(r'[^a-zA-Z0-9]+', ' ', config.book_title).strip()
        file_name += f' Vol. {volume_nr}' if volume_nr != None else ''
        file_name += '.ecmb'

        print('  ' + file_name, flush=True)

        book_uid = self._generate_book_uid()
        book = ecmbBook(config.book_type, config.book_language, book_uid, config.resize_width, config.resize_height)

        self._add_meta_data(book, volume_nr)
        self._set_cover(book, resize_method, volume_dir)
        self._add_content(book, resize_method, chapter_list)

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        book.write(self._output_dir + file_name)

        print('', flush=True)


    def _set_cover(self, book: ecmbBook, resize_method: ecmbBuilderResizeBase, volume_dir: str) -> None:
        volume_dir = self._source_dir + volume_dir

        image_list = ecmbBuilderUtils.list_files(volume_dir, None, r'^(f|front|cover_front)[.](jpg|jpeg|png|webp)$', 0)
        if len(image_list):
            image_path = image_list[0]['path'] + image_list[0]['name']
            image = resize_method.process(image_path)
            book.content.set_cover_front(image[0])

        image_list = ecmbBuilderUtils.list_files(volume_dir, None, r'^(r|rear|cover_rear)[.](jpg|jpeg|png|webp)$', 0)
        if len(image_list):
            image_path = image_list[0]['path'] + image_list[0]['name']
            image = resize_method.process(image_path)
            book.content.set_cover_rear(image[0])
            

    
    def _add_content(self, book: ecmbBook, resize_method: ecmbBuilderResizeBase, chapter_list: list) -> None:
        for chapter in tqdm(chapter_list, desc='  add content'):
            folder = book.content.add_folder(chapter['path'])
            image_list = ecmbBuilderUtils.list_files(chapter['path'], r'^(?!__).+$', r'^(?!__).+[.](jpg|jpeg|png|webp)$', 0)
            for image in image_list:
                image_path = chapter['path'] + image['name']
                image = resize_method.process(image_path)
                if len(image) == 3:
                    folder.add_image(image[0], image[1], image[2], unique_id=image_path)
                else:
                    folder.add_image(image[0], unique_id=image_path)
            
            target = None
            target_side = None
            if chapter.get('start_with'):
                start_with = chapter.get('start_with').split('#')
                target = chapter['path'] + start_with[0]
                target_side = start_with[1] if len(start_with) == 2 else None

            book.navigation.add_chapter(chapter.get('label'), folder, target, target_side, chapter.get('title'))


    def _add_meta_data(self, book: ecmbBook, volume_nr: int = None) -> None:
        config = self._book_config
        meta_data = config.meta_data
        based_on = meta_data['based_on']

        book.metadata.set_title(config.book_title)
        book.metadata.set_volume(volume_nr)
        book.metadata.set_isbn(meta_data.get('isbn'))
        book.metadata.set_publishdate(meta_data.get('publishdate'))
        book.metadata.set_description(meta_data.get('description'))

        if type(meta_data.get('publisher')) == dict and meta_data['publisher'].get('name'):
            book.metadata.set_publisher(meta_data['publisher'].get('name'), href = meta_data['publisher'].get('href'))

        if type(meta_data.get('authors')) == list:
            for author in meta_data.get('authors'):
                if type(author) == dict and author.get('name'):
                    book.metadata.add_author(author.get('name'), author.get('type'), href = author.get('href'))

        if type(meta_data.get('genres')) == list:
            for genre in meta_data.get('genres'):
                book.metadata.add_genre(genre)

        if type(meta_data.get('warnings')) == list:
            for warning in meta_data.get('warnings'):
                book.metadata.add_content_warning(warning)

        book.based_on.set_type(based_on.get('type'))
        book.based_on.set_isbn(based_on.get('isbn'))
        book.based_on.set_publishdate(based_on.get('publishdate'))
        book.based_on.set_title(based_on.get('title'))

        if type(based_on.get('publisher')) == dict and based_on['publisher'].get('name'):
            book.based_on.set_publisher(based_on['publisher'].get('name'), href = based_on['publisher'].get('href'))

        if type(based_on.get('authors')) == list:
            for author in based_on.get('authors'):
                if type(author) == dict and author.get('name'):
                    book.based_on.add_author(author.get('name'), author.get('type'), href = author.get('href'))


    def _generate_book_uid(self) -> str:
        config = self._book_config

        hash = config.book_title + str(datetime.now())

        if type(config.meta_data.get('publisher')) == dict and config.meta_data['publisher'].get('name'):
            prefix = str(config.meta_data['publisher'].get('name'))
        else: 
            prefix = config.book_title

        prefix = re.sub(r'[^a-z0-9]', '', prefix.lower())
        return prefix + '_' + hashlib.md5(hash.encode()).hexdigest()
    
    
    def _load_resize_method(self) -> ecmbBuilderResizeBase:
        config = self._book_config

        resize_methods = self._builder_config.resize_methods
        resize_method = resize_methods[config.resize_method]

        mod = __import__(resize_method[0], globals(), locals(), [resize_method[1]], 0)
        clas = getattr(mod, resize_method[1])

        return clas(config.resize_width, config.resize_height, config.webp_compression, config.compress_all)


    def _init_book_config(self) -> None:
        (chapter_folders, volume_folders) = self._read_folder_structure()
        self._book_config.init_config(chapter_folders, volume_folders)


    def _rename_source_files(self) -> None:
        if not self._builder_config.rename:
            return
        
        (chapter_folders, volume_folders) = self._read_folder_structure()

        self._rename_path(chapter_folders, 'chapter_', 4)
        if volume_folders:
            self._rename_path(volume_folders, 'volume_', 3)

        (chapter_folders, volume_folders) = self._read_folder_structure()

        image_nr = 0
        for folder in chapter_folders:
            file_list = ecmbBuilderUtils.list_files(folder['path'] + folder['name'], r'^(?!__).+$', r'^(?!__).+[.](jpg|jpeg|png|webp)$', 0)
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


    def _read_folder_structure(self) -> None:
        folder_list = ecmbBuilderUtils.list_dirs(self._source_dir, r'^(?!__).+$', 2)
        level0_folders = []
        level1_folders = []
        for folder in folder_list:
            if folder['level'] == 0:
                level0_folders.append(folder)
            else:
                level1_folders.append(folder)

        if len(level0_folders) > len(level1_folders):
            return (level0_folders, None)
        else:
            return (level1_folders, level0_folders)


    def _set_dirs(self, folder_name: str) -> None:
        source_dir = str(path.Path(self._builder_config.source_dir + folder_name).abspath()) + '\\'
        if not os.path.isdir(source_dir):
            raise ecmbException(f'Comic/Manga folder "{folder_name}" was not found!')
        
        output_dir = str(path.Path(self._builder_config.output_dir + folder_name).abspath()) + '\\'
        output_dir = str(path.Path(output_dir + '..\\').abspath()) + '\\'

        self._folder_name = folder_name
        self._source_dir = source_dir
        self._output_dir = output_dir
        
