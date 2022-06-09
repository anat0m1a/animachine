from pymediainfo import MediaInfo
import subprocess
import pathlib
import re
import os

class AnimeEncoder:
    def __init__(self):
        # Configuration Options
        self.srcDir = '/Users/lizzy/Movies/Sailor_Moon/'
        self.destDir = os.path.join(self.srcDir, 'Converted/')
        self.encodeOpts = ['crf=19:limit-sao:bframes=8:psy-rd=1:aq-mode=3','crf=20:bframes=8:psy-rd=1:aq-mode=3',\
                           'crf=19:bframes=8:psy-rd=1:aq-mode=3:aq-strength=0.8:deblock=1,1',\
                           'crf=19:limit-sao:bframes=8:psy-rd=1:psy-rdoq=1:aq-mode=3:qcomp=0.8',\
                           'crf=19:bframes=8:psy-rd=1:psy-rdoq=1:aq-mode=3:qcomp=0.8',\
                           'crf=16:no-sao:bframes=8:psy-rd=1.5:psy-rdoq=2:aq-mode=3:ref=6',\
                           'crf=14:preset=veryslow:no-sao:no-strong-intra-smoothing:bframes=8:'\
                           + 'psy-rd=2:psy-rdoq=1:aq-mode=3:deblock=-1,-1:ref=6']
        self.preset = ''
        self.SNUM = 1
        self.srcExt = ''
        self.destExt = ''
        self.NUM = 1
        self.tempList = []


    def run(self):

        # Detect OS and clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')

        print("""
 _     _  ____  ____ ___  _ _ ____    ____  _      _  _      _____
/ \   / \/_   \/_   \\\\  \//|// ___\  /  _ \/ \  /|/ \/ \__/|/  __/
| |   | | /   / /   / \  /   |    \  | / \|| |\ ||| || |\/|||  \  
| |_/\| |/   /_/   /_ / /    \___ |  | |-||| | \||| || |  |||  /_ 
\____/\_/\____/\____//_/     \____/  \_/ \|\_/  \|\_/\_/  \|\____\\
""")
        print("""Welcome to Lizzy\'s portable x265 anime encoding convenience script.

Before running, please ensure a version of ffmpeg with x265 is
accessible in your system path. Please also ensure you have changed the
destination directory before running the script.

Additionally, this script will pass the current working directory
into ffmpeg. If you do not want it to do this, set the srcDir
variable in the script.\n""")

        for file in os.listdir(self.srcDir):
            if file.endswith(self.srcExt):
                os.rename(self.srcDir + file, self.srcDir + getValidFilenames(file))
        
        filename = ''
        for file in os.listdir(self.srcDir):
            if file.endswith(self.srcExt):
                filename = file
                break
            else:
                continue
        
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
        + f'   7. {self.encodeOpts[6]}\n')

        # Get basic input from the user about the content
        while True:
            self.preset = int(input('Please select [1-7]: '))
            if 1 <= self.preset <= 7:
                break
            print('try again.')

        self.SNUM = getNum("\nPlease enter the season number: ")
        
        self.NUM = getNum("\nPlease enter an episode to start at (affects naming only): ")

        self.srcExt = getContainer("\nPlease specify input container (mkv, mp4, etc.): ")

        self.destExt = getContainer('\nPlease enter an output container: ')

        media_info = MediaInfo.parse(self.srcDir + filename)
        self.media_info = MediaInfo.to_data(media_info)

        for tempTrack in self.media_info['tracks']:
            if tempTrack['track_type'] == 'Text':
                self.tempList.append(tempTrack) 
                print(f"{len(self.tempList)}) {tempTrack['format']} ({tempTrack['language']}, SUBTITLE "\
                        f"........... {tempTrack['language']}  - {tempTrack['title']}")

        # To-do: merge sub selection and audio track selection into one function or code seg.
        self.subindex = -1
        while self.subindex == -1:
            try:
                self.subindex = int(input('\nPlease enter an index for the subtitle '\
                        + f'track you wish to use (0 for no subs) [0-{str(len(self.tempList))}]: '))
                if self.subindex > len(self.tempList) or self.subindex < 0:
                    print("\nPlease input a valid value.")
                    self.subindex = -1
            except ValueError:
                print("Please enter an int.")

        self.language = self.tempList[self.subindex-1]['language']
        self.title = self.tempList[self.subindex-1]['title']

        for tempTrack in self.media_info['tracks']:
            if tempTrack['track_type'] == 'Audio':
                self.tempList.append(tempTrack) 
                print(f"{len(self.tempList)}) {tempTrack['format']} ({tempTrack['language']}, SUBTITLE "\
                        f"........... {tempTrack['language']}  - {tempTrack['title']}")

        self.audioindex = -1
        while self.audioindex == -1:
            try:
                self.audioindex = int(input('\nPlease enter an index for the audio '\
                    + 'track you wish to use: ')) - 1
                if self.audioindex > len(self.tempList)-1 or self.audioindex < 0:
                    print("\nPlease input a value in the valid range.")
                    self.audioindex = -1
            except ValueError:
                print("Please input an integer.")

    def checkSubs(self, file):
        self.tempList = []
        for tempTrack in self.media_info['tracks']:
            if tempTrack['track_type'] == 'Text':
                self.tempList.append(tempTrack) 
                if self.language == tempTrack['language'] or self.title == tempTrack['title']:
                    self.subindex = len(self.tempList)

        """to be updated in the future - this essentially prefers the title of the subs over the
        language to ensure that regardless of the index of the subs, the most optimal subtitle
        track is chosen based on the initial chosen index"""

        if self.tempList[self.subindex-1]['format'] in {'ASS', 'UTF-8'}:
            self.subtype = 1
        elif self.tempList[self.subindex-1]['format'] == 'PGS':
            self.subtype = 2
        else:
            print('error')

    def encode(self):
        OUTNAME = ''
        onemin = False
        test = str(input('1 min dummy encode? [Y]/n '))
        if test in {'Y', 'y', ''}:
            onemin = True
        for file in os.listdir(self.srcDir):
            if file.endswith(self.srcExt):
                S = 'S' + str(self.SNUM).zfill(2) if self.SNUM < 10 else 'S' + str(self.SNUM)
                E = 'E' + str(self.NUM).zfill(2) if self.NUM < 10 else 'E' + str(self.NUM)
                OUTNAME = S + E
                self.checkSubs(file)
                file = self.srcDir + file
                if self.subtype == 1:
                    subprocess.call(['ffmpeg', *(['-t', '00:01:00'] if onemin else []), '-i', file, \
                                        '-c:v', 'libx265', '-x265-params', self.encodeOpts[self.preset], '-preset', 'slow', \
                                        '-vf', f'subtitles={file}:stream_index={str(self.subindex-1)}', \
                                        '-c:a', 'libopus', '-b:a', '96k', '-ac', '2', '-map', \
                                        '0:v:0', '-map', '0:a:'+str(self.audioindex), str(self.destDir) + OUTNAME + '.' \
                                        + self.destExt])
                    if onemin == True:
                        break
                elif self.subtype == 2:
                    subprocess.call(['ffmpeg', *(['-t', '00:01:00'] if onemin else []), '-i', file, '-c:v', 'libx265', \
                                        '-x265-params', self.encodeOpts[self.preset], '-preset', 'slow', '-filter_complex', \
                                        '[0:v][0:s:'+str(self.subindex-1)+']overlay[v]', '-map', '[v]', '-c:a', \
                                        'libopus', '-b:a', '96K', '-ac', '2', '-map', \
                                        '0:a:'+str(self.audioindex), str(self.destDir) + OUTNAME + '.' + self.destExt])
                    if onemin == True:
                        break
                else:
                    subprocess.call(['ffmpeg', *(['-t', '00:01:00'] if onemin else []), '-i', file, \
                                        '-c:v', 'libx265', '-x265-params', self.encodeOpts[self.preset], '-preset', 'slow', \
                                        '-c:a', 'libopus', '-b:a', '96K', '-ac', '2', '-map', '0:v', \
                                        '-map', '0:a:'+str(self.audioindex), str(self.destDir) + OUTNAME + '.' + self.destExt])
                    if onemin == True:
                        break
                NUM +=1


def getContainer(m):
    valCont = ['mkv', 'mp4', 'mov', 'avi', 'webm', 'mpg', 'wmv', 'm4v', 'm2ts']
    while True:
        cont = input(m)
        if cont in valCont:
            return cont
        else:
            print("\nInvalid. Supported containers are: ")
            for i in range(len(valCont)): print(valCont[i])
            continue

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

def main():
    anime_encoder = AnimeEncoder()
    anime_encoder.run()
    anime_encoder.encode()

if __name__ == "__main__":
    main()