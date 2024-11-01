import glob, os
import sys
from mutagen.mp3 import MP3
from moviepy.editor import *
from transliterate import get_available_language_codes
from transliterate import translit
import numpy as np
from pathlib import Path
from mp3_tagger import MP3File

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
        #self.metadata=eyed3.load(self.filepath)   
        self.metadata=MP3File(self.filepath).get_tags()
        
        #print(self.metadata)
        
        if(self.metadata['ID3TagV1']['song']!=""):
            self.title = self.metadata['ID3TagV1']['song']
        if(self.metadata['ID3TagV1']['album']!=""):
            self.album = self.metadata['ID3TagV1']['album']
        if(self.metadata['ID3TagV2']['artist']!=""):
            self.artist = self.metadata['ID3TagV2']['artist']
        #    print(self.album)
        # if(self.metadata.tag.artist!=""):  self.artist = self.metadata.ID3TagV2.artist
        if(self.metadata['ID3TagV2']['year']):
            self.year = self.metadata['ID3TagV2']['year']
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
    
    def __init__(self, al_path, _settings = {}):

        img_paths = glob.glob(al_path+"*.jpg")
        self.logo = img_paths[0]
        self.settings = _settings

        self.artist = ''    # the artist
        self.title = ""     # album name
        self.year = 0       # release year


        self.path = al_path
        self.tracks = []
        self.fulltime = 0
        self.audioclips = []
        directory = al_path + "*.mp3"
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
        if(self.year==0): self.year = track.year;

    def print_tracklist(self):
        num = 1
        print(self.getFullTitle())
        resstr = "Треклист: \n"        
        for track in self.tracks:
            resstr+='{} - {}. {}\n'.format(track.gettime(),num,track.title)
            num += 1
        with open(self.path+"tracklist.txt", "w") as file:
            file.write(resstr)
        print(resstr)

    def getFullTitle(self):
        if((self.title=="") & (self.artist=="")): 
            return "full_album"
        
        return "{} - {} ({} LP)".format(self.artist, self.title, self.year)

    def render_video(self):
        video_clip = ImageClip(self.logo , duration = self.fulltime)# concatenate_videoclips(images, method="compose")
        video_clip = video_clip.set_audio(concatenate_audioclips(self.audioclips))  
        
        logo_opts = self.settings['logo'].args
#        print(logo_opts)
        if(logo_opts['path']!='no'):
            logo = (ImageClip(logo_opts['path'])
                .set_duration(video_clip.duration)
            #    .resize(height=20, width=20) # if you need to resize...
                .margin(right=logo_opts['right'], top=logo_opts['top'], opacity=0) # (optional) logo-border padding
                .set_pos(("right","top")))

            video_clip = CompositeVideoClip([video_clip, logo])

        tl_opts = self.settings['tl'].args
        if(tl_opts['mode']!='no'):
            # Generate a text clip  
            txt_clip = TextClip("GfG-MoviePy",font="Arial-Narrow", fontsize = 75, color = 'green')  
    
            # setting position of text in the center and duration will be 5 seconds  
            txt_clip = txt_clip.set_pos('bottom').set_duration(5)  
    
            # Overlay the text clip on the first video clip  
            video_clip = CompositeVideoClip([video_clip, txt_clip])  


        video_clip.write_videofile(self.path+self.getFullTitle()+".mp4", fps=60)
