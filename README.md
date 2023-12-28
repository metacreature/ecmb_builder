# *.ecmb - The new Comic-Manga-eBook
**Benefits:**
- right to left reading in page-mode for mangas, while scroll-mode is still top-down
- advanced support for double-pages
- content-warnings for using safe-guard
- a bunch of possible meta-data like genres and even the homepage of the publisher ([go to example >](https://github.com/metacreature/ecmb_definition/blob/master/examples/v1.0/example_full.xml))
- support for sub-chapters and many possibilities for navigation with headlines and page-links ([go to example >](https://github.com/metacreature/ecmb_definition/blob/master/examples/v1.0/advanced_book/advanced_book.ecmb_unpacked/ecmb.xml))
- validateable via XSD
- published under [MIT License](https://choosealicense.com/licenses/mit/)

## The project ([https://metacreature.github.io/ecmb](https://metacreature.github.io/ecmb))
**It contains:**
- the [definition](https://github.com/metacreature/ecmb_definition) of the file-format and a file-validator
- a [library](https://github.com/metacreature/ecmblib_python) for packing the eBooks
- a [builder](https://github.com/metacreature/ecmb_builder) for building the eBooks from your source-images
- a mobile-app for reading the eBooks is under developement
- unfortunately there is no web-scraper to download source-images, coz I guess that would be illegal in my country to publish something like that. Maybe you'll find some here: [https://github.com/topics/manga-scraper](https://github.com/topics/manga-scraper)

**If you like it I would be happy if you  [donate on checkya](https://checkya.com/1hhp2cpit9eha/payme)**


## About this repository:
This is a easy-to-use builder to build *.ecmb-files from your source-images without knowing anything about programming.

# Using the builder

### Installation
- download and install Python3 (>=3.11) [https://www.python.org/downloads/](https://www.python.org/downloads/)
- download and install Git [https://git-scm.com/downloads](https://git-scm.com/downloads).
  Here is a little guide how to install and open git console: [https://www.youtube.com/watch?v=lKYtK-DS0MY](https://www.youtube.com/watch?v=lKYtK-DS0MY)
- create an empty folder on your harddisk (eg. "comic_manga") and open it
- open the git-console with right-click (like you learned in the video) and then type or copy the commands to the console and press [enter] after each command:
    - `mkdir source_dir`
    - `mkdir output_dir`
    - `git clone git@github.com:metacreature/ecmb_builder.git`
    - `cd ecmb_builder`
    - `pip install -r requirements.txt`
- after that there are 3 subfolders in your "comic_manga"-folder
- open the folder "ecmb_builder" and open the config-file `ecmb_builder_config.yml` with any simple text-editor
  (I would recommend to use [https://notepad-plus-plus.org/downloads/](https://notepad-plus-plus.org/downloads/)) and do your settings there (or just leave it as it is).

### Building your first book
Your source-files have to be stored in "comic_manga/source_dir" (if you didn't specify a different one in the config-file)

File-Structure:
```
source_dir/
    ˪ My_Manga_Name
        ˪ chapter_001
             ˪ img_00001.jpg
             ˪ img_00002.jpg
             ˪ img_00003.jpg
             ˪ img_00004.jpg
        ˪ chapter_002
        ˪ chapter_003
        ˪ chapter_004
        ˪ cover_front.jpg
        ˪ cover_rear.jpg
```
or 
```
source_dir/
    ˪ My_Manga_Name
        ˪ volume_01
            ˪ chapter_001
               ˪ img_00001.jpg
               ˪ img_00002.jpg
               ˪ img_00003.jpg
               ˪ img_00004.jpg
            ˪ chapter_002
            ˪ chapter_003
            ˪ chapter_004
            ˪ cover_front.jpg
            ˪ cover_rear.jpg
```
The file-names can be messy - if you activated "rename" in the config-file, it will be renamed anyways. Files starting with "__" (2 underscores) are ignored in general.
The cover-images have to have one of these names:
| cover_front.jpeg | cover_rear.jpeg |
| cover_front.jpg  | cover_rear.jpg  |
| cover_front.png  | cover_rear.png  |
| cover_front.webp | cover_rear.webp |
| front.jpeg       | rear.jpeg       |
| front.jpg        | rear.jpg        |
| front.png        | rear.png        |
| front.webp       | rear.webp       |
| f.jpeg           | r.jpeg          |
| f.jpg            | r.jpg           |
| f.png            | r.png           |
| f.webp           | r.webp          |

