import re, os, yaml, io, path, json, hashlib
from datetime import datetime
from .ecmb_builder_utils import ecmbBuilderUtils
from .ecmblib.ecmb import ecmbBook, ecmbUtils, ecmbException, BOOK_TYPE, BASED_ON_BOOK_TYPE, CONTENT_WARNING, AUTHOR_TYPE, ALLOWED_IMAGE_EXTENTIONS 


class ecmbBuilder():

    _working_dir = None
    _rename = None

    _source_dir = None
    _is_initialized = None
    _book_config = None

    _has_volumes = None
    _volume_folders = None
    _chapter_folders = None


    def __init__(self):
        self._load_config()


    def initialize(self, folder_name: str) -> None:
        self._set_source_dir(folder_name)
        self._read_book_config()
        if self._is_initialized:
            raise ecmbException('Book is allready initialized!')
        self._read_folder_structure()
        self._rename_source_files()
        self._init_book_config(folder_name)


    def build(self, folder_name: str, volumes: int|list[int]) -> None:
        pass


    def _init_book_config(self, folder_name: str) -> None:
        book_type = ecmbUtils.enum_values(BOOK_TYPE)
        warnings = ecmbUtils.enum_values(CONTENT_WARNING)
        based_on_book_type = ecmbUtils.enum_values(BASED_ON_BOOK_TYPE)
        authors = ecmbUtils.enum_values(AUTHOR_TYPE)
        authors = [{'name': '', 'type': at, 'href': ''} for at in authors]

        book_config = {
            'type': '|'.join(book_type),
            'language': 'en',
            'image_width': 900,
            'image_height': 1200,
            'isbn': '',
		    'publisher': {
                'name': '',
                'href': ''
            },
            'publishdate': '1900-01-31',
            'title':  re.sub(r'[^a-zA-Z0-9]+', ' ', folder_name).strip(),
            'description': '',
            'authors': authors,
		    'genres': [],
		    'warnings': warnings,
            'basedon': {
                'type': '|'.join(based_on_book_type),
                'isbn': '',
                'publisher': {
                    'name': '',
                    'href': ''
                },
                'publishdate': '1900-01-31',
                'title': '',
                'authors': authors
            }
        }

        chapter_cnt = 0
        chapter_template = {
            'label': '',
            'title': '',
            'start_with': 'my_image_name.jpg#left'
        }

        if self._has_volumes:
            book_config['volumes'] = {}
            for volume in self._volume_folders:
                book_config['volumes'][volume['name']] = {}
                volume_path = volume['path'] + volume['name'] + '\\'
                for chapter in self._chapter_folders:
                    if chapter['path'] == volume_path:
                        chapter_cnt += 1
                        chapter_template.update({'label': f'Chapter {chapter_cnt}'})
                        book_config['volumes'][volume['name']][chapter['name']] = dict(chapter_template)
        else: 
            book_config['chapters'] = {}
            for chapter in self._chapter_folders:
                chapter_cnt += 1
                chapter_template.update({'label': f'Chapter {chapter_cnt}'})
                book_config['chapters'][chapter['name']] = dict(chapter_template)

        with open(self._source_dir + 'book_config.json', 'w') as f:
            json.dump( book_config, f, indent=4)


    def _rename_source_files(self) -> None:
        if not self._rename:
            return
        
        self._rename_path(self._chapter_folders, 'chapter_', 4)
        if self._has_volumes:
            self._rename_path(self._volume_folders, 'volume_', 3)

        self._read_folder_structure()

        image_nr = 0
        for folder in self._chapter_folders:
            file_list = ecmbBuilderUtils.list_files(folder['path'] + folder['name'], None, '^(__ecmbbuilder_tmpname_|(?!__)).+[.](jpg|jpeg|png|webp)$', 0)
            image_nr = self._rename_path(file_list, 'img_', 6, '0', image_nr)


    def _rename_path(self, path_list: list, prefix:str, zfill: int, suffix:str = '', start_at: int = 0) -> int:
        tmp_name = '__ecmbbuilder_tmpname_' + hashlib.md5(str(datetime.now()).encode()).hexdigest() + '_'

        try:
            cnt = start_at
            for item in path_list:
                cnt += 1
                new_name = tmp_name + (str(cnt).zfill(zfill))
                new_name += '.' + item.get('extension') if item.get('extension') else ''
                os.rename(item['path'] + item['name'], item['path'] + new_name)
                item['name'] = new_name

            cnt = start_at
            for item in path_list:
                cnt += 1
                new_name = prefix + (str(cnt).zfill(zfill)) + suffix
                new_name += '.' + item.get('extension') if item.get('extension') else ''
                os.rename(item['path'] + item['name'], item['path'] + new_name)
        except PermissionError:
            raise ecmbException('Permission denied for rename folders/images. Please close opened files and folders!')

        return start_at + cnt


    def _read_folder_structure(self) -> None:
        folder_list = ecmbBuilderUtils.list_dirs(self._source_dir, '^(__ecmbbuilder_tmpname_|(?!__)).+', 2)
        level0_folders = []
        level1_folders = []
        for folder in folder_list:
            if folder['level'] == 0:
                level0_folders.append(folder)
            else:
                level1_folders.append(folder)

        if len(level0_folders) > len(level1_folders):
            self._has_volumes = False
            self._volume_folders = None
            self._chapter_folders = level0_folders
        else:
            self._has_volumes = True
            self._volume_folders = level0_folders
            self._chapter_folders = level1_folders


    def _read_book_config(self) -> None:
        self._book_config = None
        self._is_initialized = False
        if os.path.exists(self._source_dir + 'book_config.json'):
            try:
                with open(self._source_dir + 'book_config.json', 'r') as f:		
                    self._book_config = json.load(f)
            except Exception as e:
                raise ecmbException('Load "book_config.json" failed: ' + str(e))
            self._is_initialized = True


    def _set_source_dir(self, folder_name: str) -> None:
        self._source_dir = None
        source_dir = str(path.Path(self._working_dir + folder_name).abspath()) + '\\'
        if not os.path.isdir(source_dir):
            raise ecmbException(f'Comic/Manga folder "{folder_name}" was not found!')
        self._source_dir = source_dir
        

    def _load_config(self) -> None:
        builder_path = str(path.Path(__file__).abspath().parent.parent) + '\\'

        try: 
            with open(builder_path + 'ecmb_builder_config.yml', 'r') as file:
                config = yaml.safe_load(file)
        except:
            raise ecmbException('Config not found or invalid!')
        
        # working-dir
        working_dir = config.get('working_dir')
        if not working_dir:
            raise ecmbException('Config: working-dir is not defined!')

        if not re.search(r'[:]', working_dir):
            working_dir = builder_path + working_dir

        self._working_dir = str(path.Path(working_dir).abspath()) +  '\\'
        
        if not os.path.isdir(self._working_dir ):
            raise ecmbException('Config: working-dir was not found!')

        # other config
        self._rename = True if config.get('rename') else False
