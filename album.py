'''
makes album in mp4 format from folder of mp3 files and cover image
'''
import glob, os
import sys
from mutagen.mp3 import MP3
from moviepy.editor import *
from transliterate import get_available_language_codes
from transliterate import translit
import numpy as np
from pathlib import Path
import ctypes
import eyed3

currdir = ""
if len (sys.argv) > 1:
    currdir = sys.argv[1] 
    #print(currdir)

def convert_seconds(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

# Функция для замены нескольких значений
def multiple_replace(target_str, replace_values):
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():
        # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)
    return target_str
    


class Track:
    
    def __init__(self, fpath):
        self.filepath = fpath
        self.title = ""
        self.artist = ""
        self.album = ""
        self.year = 0
        self.try_get_metadata()
        if(self.title==""):
            self.title = self.parse(fpath)            
        self.audio = MP3(fpath)
        self.time = self.audio.info.length
        self.position = 0
        self.AudioClip = AudioFileClip(fpath)

    def try_get_metadata(self):
        self.metadata=eyed3.load(self.filepath)     
        #print(self.metadata.tag.year)  
        if(self.metadata.tag.title!=""):
            self.title = self.metadata.tag.title
        if(self.metadata.tag.album!=""):
            self.album = self.metadata.tag.album
        #    print(self.album)
        if(self.metadata.tag.artist!=""):
            self.artist = self.metadata.tag.artist
        if(self.artist==""):
            self.artist = self.metadata.tag.album_artist
    #    if(self.year==0): self.year = self.metadata.tag.getYear() 

    def parse(self, fpath):
        track_str = str.replace(os.path.splitext(str(fpath))[0]," - ","_-_")
        track_str = track_str[track_str.find("_-_")+3:]
        track_str = multiple_replace(translit(multiple_replace(track_str, {"ya": "я","Ya": "Я","_":" ","jj":"й","(musportal.org)":""}), 'ru'), 
            {"Интро":"(Intro)","Оутро":"(Outro)"});
        return track_str

    #Тайм-код из тройки
    def timecode(self,hours, minutes,seconds):
        if(int(hours)==0): 
            return '{}:{}'.format(minutes, seconds)
        return '{}:{}:{}'.format(hours, minutes, seconds)  

    def gettime(self):
        hours, minutes, seconds = convert_seconds(self.position).split(":")
        return self.timecode(hours, minutes, seconds)
    
    def get_number_of_filename(fname):
        basename = Path(fname).stem
        return int(basename[:basename.find(".")]) 

class Album:    
    
    def __init__(self, al_path):

        img_paths = glob.glob(al_path+"*.jpg")
        self.logo = img_paths[0]

        self.artist = ''    # the artist
        self.title = ""     # album name
        self.year = 0       # release year


        self.path = al_path
        self.tracks = []
        self.fulltime = 0
        self.audioclips = []
        directory = currdir + "*.mp3"
        file_paths = sorted(glob.glob(directory, recursive=False), key=Track.get_number_of_filename )
        track_pos = 0
        for mp3_file in file_paths:
            newtrack = Track(mp3_file)
            newtrack.position = self.fulltime
            self.fulltime += newtrack.time
            self.gather_from_track(newtrack)
            self.tracks.append(newtrack)
            self.audioclips.append(newtrack.AudioClip)

    def gather_from_track(self, track: Track):
        if(self.artist==""):
            self.artist = track.artist
        if(self.title==""):
            self.title = track.album
        #if(self.year==0): self.year = track.metadata.tag.year;

    def print_tracklist(self):
        num = 1
        print(self.getFullTitle())
        print("Треклист: ")
        for track in self.tracks:
            print('{} - {}. {}'.format(track.gettime(),num,track.title))
            num += 1

    def getFullTitle(self):
        if((self.title=="") & (self.artist=="")): 
            return "full_album"
        
        return "{} - {} ({} LP)".format(self.artist, self.title, self.year)

    def render_video(self):
        video_clip = ImageClip(self.logo , duration = self.fulltime)# concatenate_videoclips(images, method="compose")
        video_clip = video_clip.set_audio(concatenate_audioclips(self.audioclips))  
        video_clip.write_videofile(self.path+self.getFullTitle()+".mp4", fps=60)

album = Album(currdir)
album.print_tracklist()
#album.render_video()