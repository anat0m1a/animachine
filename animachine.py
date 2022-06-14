#Copyright (c) 2022 Elizabeth Watson <lizzyrwatson1@gmail.com>

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import pathlib
from ffpb import ProgressNotifier
from pymediainfo import MediaInfo
from tqdm import tqdm
import subprocess
import signal
import sys
import re
import os

class AnimeEncoder:
    def __init__(self):
        # Configuration Options
        self.encodeOpts = ['crf=19:limit-sao:bframes=8:psy-rd=1:aq-mode=3:preset=slow',\
                           'crf=20:bframes=8:psy-rd=1:aq-mode=3:preset=slow',\
                           'crf=19:bframes=8:psy-rd=1:aq-mode=3:aq-strength=0.8:deblock=1,1:preset=slow',\
                           'crf=19:limit-sao:bframes=8:psy-rd=1:psy-rdoq=1:aq-mode=3:qcomp=0.8:preset=slow',\
                           'crf=19:bframes=8:psy-rd=1:psy-rdoq=1:aq-mode=3:qcomp=0.8:preset=slow',\
                           'crf=16:no-sao:bframes=8:psy-rd=1.5:psy-rdoq=2:aq-mode=3:ref=6:preset=slow',\
                           'crf=14:preset=veryslow:no-sao:no-strong-intra-smoothing:bframes=8:'\
                           + 'psy-rd=2:psy-rdoq=1:aq-mode=3:deblock=-1,-1:ref=6',\
                           'aq-mode=3:sao:strong-intra-smoothing:crf=17:preset=veryslow']
        self.srcDir = ''
        self.destDir = ''
        self.preset = ''
        self.SNUM = 1
        self.srcExt = ''
        self.destExt = ''
        self.NUM = 1
        self.subsList = []
    

    def __exit__(self, exc_type, exc_value, traceback):
        pass
    

    def __enter__(self):
        return self


    def run(self):

        # Detect OS and clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')

        print("""
   __ _               _        _         _                      _     _            
  / /(_)_________   _( )__    /_\  _ __ (_)_ __ ___   __ _  ___| |__ (_)_ __   ___ 
 / / | |_  /_  / | | |/ __|  //_\\\\| '_ \| | '_ ` _ \ / _` |/ __| '_ \| | '_ \ / _ \\
/ /__| |/ / / /| |_| |\__ \ /  _  \ | | | | | | | | | (_| | (__| | | | | | | |  __/
\____/_/___/___|\__, ||___/ \_/ \_/_| |_|_|_| |_| |_|\__,_|\___|_| |_|_|_| |_|\___|
                |___/                                                                                                                          
""")
        print("""Welcome to Lizzy\'s portable x265 anime encoding convenience script.

The concept for this script originated from Kokomin's "Anime on a Technical Level - 
Anime Encoding Guide for x265 (HEVC) & AAC/OPUS (and Why to Never Use FLAC)", which
can be found here: 

https://kokomins.wordpress.com/2019/10/10/anime-encoding-guide-for-x265-and-why-to-never-use-flac/

Before running, please ensure a version of ffmpeg with x265 is
accessible in your system path.

*** potentilly destructive actions ahead ***

This script will sanitise the filenames in the source directory
by replacing spaces and terminal-unfriendly characters with underscores
or by removing them entirely. If you do not want this, exit now.\n""")

        input("Please press enter to proceed.")
        p = pathlib.Path()
        if self.srcDir == '' or os.path.isdir(self.srcDir) is False:
            while True:
                r = str(input('\nSource directory set to null or path invalid.\n'\
                            f"[{p.absolute()}] will be used. Is this okay? [Y/n]: "))
                if r in {'Y', 'y', ''}:
                    self.srcDir = pathlib.Path(p.absolute())
                    break
                if r in {'N', 'n'}:
                    self.srcDir = dirCheck('\nPlease enter a new src dir:\n')
                    break
                else:
                    print('\nPlease enter y or n')

        if self.destDir == '' or os.path.isdir(self.destDir) is False:
            while True:
                r = str(input('\nThe dest dir variable has not been set. '\
                            f'Would you like to\ncreate the Converted dir in {self.srcDir}? [Y/n]: '))
                if r in {'Y', 'y', ''}:
                    self.destDir = os.path.join(self.srcDir, 'Converted/')
                    if os.path.isdir(self.destDir):
                        break
                    os.mkdir(self.destDir)
                    break
                elif r in {'N', 'n'}:
                    self.destDir = dirCheck('\nPlease enter a new dest dir:\n')
                    break
                else:
                    print('\nPlease enter y or n')

        self.srcDir = self.srcDir if str(self.srcDir).endswith(os.path.sep) else str(self.srcDir) + os.path.sep
        self.destDir = self.destDir if str(self.destDir).endswith(os.path.sep) else str(self.destDir) + os.path.sep

        input(f'Using srcDir: {self.srcDir}\n'\
             +f'Using destDir: {self.destDir}\n\n'\
             +'Ok to continue? [enter] If not, please exit and try again.') 
        
        print('\nSelect your preset preference:\n\n'\
        +  'A. Settings to rule them all:\n\n'\
        + f'   1. {self.encodeOpts[0]} (higher bitrate)\n'\
        + f'   2. {self.encodeOpts[1]} (more compression)\n\n'\
        +  'B. Flat, slow anime (slice of life, everything is well-lit):\n\n'\
        + f'   3. {self.encodeOpts[2]}\n\n'\
        +  'C. Some dark scenes, some battle scenes (shonen, historical, etc.):\n\n'\
        + f'   4. {self.encodeOpts[3]} (motion + fancy & detailed FX)\n'\
        + f'   5. {self.encodeOpts[4]} (non-complex, motion only alternative)\n\n'\
        +  'D. Movie-tier dark scene, complex grain/detail, and BDs with dynamic-grain\n'\
        +  '   injected debanding:\n\n'\
        + f'   6. {self.encodeOpts[5]}\n\n'\
        +  'E. I have infinite storage, a supercomputer, and I want details:\n\n'\
        + f'   7. {self.encodeOpts[6]}\n\n'
        +  'F. Generic TV/Movie Preset:\n\n'\
        + f'   8. {self.encodeOpts[7]}\n')

        # Get basic input from the user about the content
        while True:
            self.preset = int(input(f'Please select [1-{len(self.encodeOpts)}]: ')) - 1
            if 1 <= self.preset <= len(self.encodeOpts):
                break
            print('try again.')

        self.SNUM = getNum("\nPlease enter the season number: ")
        
        self.NUM = getNum("\nPlease enter an episode to start at (affects naming only): ")

        if self.srcExt == '':
            self.srcExt = getContainer("\nPlease specify input container (mkv, mp4, etc.): ")

        if self.destExt == '':
            self.destExt = getContainer('\nPlease enter an output container: ')

        for file in os.listdir(self.srcDir):
            if file.endswith(self.srcExt):
                os.rename(self.srcDir + file, self.srcDir + getValidFilenames(file))
        
        self.filename = ''
        for file in sorted(os.listdir(self.srcDir)):
            if file.endswith(self.srcExt):
                self.filename = file
                break

        self.getSubs()
        for tempTrack in range(len(self.subsList)):
            self.langTrack = self.subsList[tempTrack].get('language')
            self.titleTrack = self.subsList[tempTrack].get('title')
            print(f"{tempTrack + 1}) {self.subsList[tempTrack]['format']} "\
                        f"({self.subsList[tempTrack]['language'] if self.langTrack else '[no language detected]'},"\
                        f"SUBTITLE ........... {self.subsList[tempTrack]['language'] if self.langTrack else '[no language detected]'} - "\
                        f"{self.subsList[tempTrack]['title'] if self.titleTrack else '[no title detected]'}")

        # To-do: merge sub selection and audio track selection into one function or code seg.
        self.subindex = -1
        while self.subindex == -1:
            try:
                self.subindex = int(input('\nPlease enter an index for the subtitle '\
                        + f'track you wish to use (0 for no subs) [0-{str(len(self.subsList))}]: '))
                if self.subindex > len(self.subsList) or self.subindex < 0:
                    print("\nPlease input a valid value.")
                    self.subindex = -1
            except ValueError:
                print("Please enter an int.")

        # Set the language and title preferences going forwards
        self.language = self.subsList[self.subindex-1]['language'] if self.langTrack else ''
        self.title = self.subsList[self.subindex-1]['title'] if self.titleTrack else ''
        i = 0
        for tempTrack in self.media_info['tracks']:
            self.langTrack = tempTrack.get('language')
            self.titleTrack =tempTrack.get('title')
            if tempTrack['track_type'] == 'Audio':
                i+=1
                self.subsList.append(tempTrack) 
                print(f"{i}) {tempTrack['format']} "\
                        f"({tempTrack['language'] if self.langTrack else '[no language detected]'},"\
                        f" AUDIO ........... {tempTrack['language']} - "\
                        f"{tempTrack['title'] if self.titleTrack else '[no title detected]'}")

        self.audioindex = -1
        while self.audioindex == -1:
            try:
                self.audioindex = int(input('\nPlease enter an index for the audio '\
                    + 'track you wish to use: ')) - 1
                if self.audioindex > len(self.subsList)-1 or self.audioindex < 0:
                    print("\nPlease input a value in the valid range.")
                    self.audioindex = -1
            except ValueError:
                print("Please input an integer.")

        OUTNAME = ''
        testEncode = False
        test = str(input('3 min dummy encode? [Y]/n '))
        if test in {'Y', 'y', ''}:
            testEncode = True
        for file in sorted(os.listdir(self.srcDir)):
            if file.endswith(self.srcExt):
                S = 'S' + str(self.SNUM).zfill(2) if self.SNUM < 10 else 'S' + str(self.SNUM)
                E = 'E' + str(self.NUM).zfill(2) if self.NUM < 10 else 'E' + str(self.NUM)
                OUTNAME = S + E
                self.checkSubs()
                file = self.srcDir + file
                
                with ProgressNotifier (file=sys.stderr, encoding=None, tqdm=tqdm,
                                    source=OUTNAME) as notifier:

                    p = subprocess.Popen(['ffmpeg', *(['-t', '00:03:00'] if testEncode else []), \
                                    '-i', file, '-c:v', 'libx265', '-x265-params', \
                                    self.encodeOpts[self.preset], \
                                    *(['-vf', f'subtitles={file}:stream_index='\
                                    + str(self.subindex-1), '-map', '0:v:0'] \
                                    if self.subtype == 1 else (['-filter_complex', \
                                    f'[0:v][0:s:{str(self.subindex-1)}]overlay[v]', \
                                    '-map', '[v]'] if self.subtype == 2 else [])), \
                                    '-c:a', 'libopus', '-b:a', '96k', '-ac', '2', '-map', \
                                    f'0:a:{str(self.audioindex)}', f'{str(self.destDir)}' \
                                    + f'{OUTNAME}.{self.destExt}'], stderr = subprocess.PIPE)

                    while True:
                        out = p.stderr.read(1)
                        if out == b"" and p.poll() is not None:
                            break
                        if out != b"":
                            notifier(out)
                if testEncode:
                    break
                self.NUM += 1

    def getSubs(self):
        self.media_info = MediaInfo.to_data(MediaInfo.parse(self.srcDir + self.filename))
        self.subsList = []
        for tempTrack in self.media_info['tracks']:
            if tempTrack['track_type'] == 'Text':
                self.subsList.append(tempTrack)


    def checkSubs(self):
        self.getSubs()

        if self.subsList[self.subindex-1]['format'] in {'ASS', 'UTF-8'}:
            self.subtype = 1
        elif self.subsList[self.subindex-1]['format'] == 'PGS':
            self.subtype = 2
        else:
            raise FormatError(self.filename, self.subsList[self.subindex-1]['format'])
        
        self.titleTrack = ''
        self.langTrack = ''
        for tempTrack in range(len(self.subsList)):
            self.langTrack = self.subsList[tempTrack].get('language')
            self.titleTrack = self.subsList[tempTrack].get('title')
            if self.titleTrack:
                if self.title == self.titleTrack:
                    self.subindex = tempTrack + 1
                    return
            if self.langTrack:
                if self.language == self.langTrack:
                    self.subindex = tempTrack + 1
                    return
        raise FileMatchError(self.filename, self.title, self.language)


def getContainer(m):
    valCont = ['mkv', 'mp4', 'mov', 'avi', 'webm', 'mpg', 'wmv', 'm4v', 'm2ts']
    while True:
        cont = input(m)
        if cont in valCont:
            return cont
        print("\nInvalid. Supported containers are: ")
        for i in enumerate(valCont): print(valCont[i])


def getValidFilenames(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def getNum(m):
    while True:
        num = 0
        try:
            num = int(input(m))
        except ValueError:
            print('must be int')
        if num > 0:
            return num


def dirCheck(msg):
    while True:
        r = str(input(msg))
        dirCheck = os.path.isdir(r)
        if dirCheck:
            return r
        print('\nNot a valid dir. Try again.')


def main():
    try:
        with AnimeEncoder() as encoder:
            encoder.run()
    except KeyboardInterrupt:
        print('\nExiting.')
        return signal.SIGINT + 128 # POSIX Standard
    except Exception as err:
        print('Unexpected exception:', err)
        return 1

class FileMatchError(Exception):
    def __init__(self, f, title, language, *args):
        super().__init__(args)
        self.f = f
        self.title = title
        self.language = language

    def __str__(self):
        return f'The file {self.f} does not contain matching title and/or language tracks: [{self.title}] [{self.language}]'

class FormatError(Exception):
    def __init__(self, f, format, *args):
        super().__init__(args)
        self.f = f
        self.format = format

    def __str__(self):
        return f'The file {self.f} contains an unsupported subtitle format: [{self.format}]'

if __name__ == "__main__":
    main()
