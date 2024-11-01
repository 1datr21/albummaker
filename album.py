'''
makes album in mp4 format from folder of mp3 files and cover image
'''

from argman import ArgManager
import ctypes
from api import Album
import sys




argv_keys = {'dir':{'path':'no'},
             'logo':{'path':'no','right':8, 'top': 20},
             'tl':{'mode':'no'}}

argman = ArgManager(sys.argv, argv_keys)
print(argman.args['dir'].args)

if(argman.args['dir'].args['path']!=""):
    if(argman.args['dir'].args['path'][-1]!="\\"): argman.args['dir'].args['path'] = argman.args['dir'].args['path']+"\\"

print(argman.args)
#print(sys.argv)
if len(sys.argv)==1:
    print('''
    --dir <directory> - set directory of album
    --watermark <path> - set watermark picture (default no)
    --tl <tltype> - tracklist (default no) values : no, simple, righttable
''')
    exit(0)


album = Album(argman.args['dir'].args['path'],{'logo':argman.args['logo'],'tl':argman.args['tl']})
album.print_tracklist()
album.render_video()