import os
import subprocess
from subprocess import check_output
import re

srcDir = '.\\'
destDir = '.\\Converted\\'

encodeOpts = ['crf=19:limit-sao:bframes=8:psy-rd=1:aq-mode=3','crf=20:bframes=8:psy-rd=1:aq-mode=3',\
        'crf=19:bframes=8:psy-rd=1:aq-mode=3:aq-strength=0.8:deblock=1,1',\
        'crf=19:limit-sao:bframes=8:psy-rd=1:psy-rdoq=1:aq-mode=3:qcomp=0.8',\
        'crf=19:bframes=8:psy-rd=1:psy-rdoq=1:aq-mode=3:qcomp=0.8',\
        'crf=16:no-sao:bframes=8:psy-rd=1.5:psy-rdoq=2:aq-mode=3:ref=6',\
        'crf=14:preset=veryslow:no-sao:no-strong-intra-smoothing:bframes=8:'\
        + 'psy-rd=2:psy-rdoq=1:aq-mode=3:deblock=-1,-1:ref=6']

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print('\n _      _                   _         ___          _\n'\
+ '| |    (_)                 ( )       / _ \        (_)                 \n'\
+ '| |     _  ____ ____ _   _ |/  ___  / /_\ \ _ __   _  _ __ ___    ___ \n'\
+ '| |    | ||_  /|_  /| | | |   / __| |  _  || \'_ \ | || \'_ ` _ \  / _ \ \n'\
+ '| |____| | / /  / / | |_| |   \__ \ | | | || | | || || | | | | ||  __/\n'\
+ '\_____/|_|/___|/___| \__, |   |___/ \_| |_/|_| |_||_||_| |_| |_| \___|\n'\
+ '                      __/ |                                           \n'\
+ '                     |___/                                            \n')
    print('Welcome to Lizzy\'s portable x265 anime encoding convenience script.\n\n'\
          + 'Before running, please ensure a version of ffmpeg with x265 is\n'\
          + 'accessible in your system path. Please also ensure you have changed the\n'\
          + 'destination directory before running the script.\n\n'\
          + 'Additionally, this script will pass the current working directory\n'\
          + 'into ffmpeg. If you do not want it to do this, set the srcDir\n'\
          + 'variable in the script.\n')
          
    if (destDir == ''):
        print('No destination directory detected!! Exiting...')
        quit()
        
    input('If you are ready to continue, please press ENTER. Otherwise, CTRL+C to exit.\n\n')
    
    for i in range(2): print("=" * 80)

    print('\nSelect your preset preference:\n\n'\
        + 'A. Settings to rule them all:\n\n'\
        + '   1. ' + encodeOpts[0] + ' (higher bitrate)\n'\
        + '   2. ' + encodeOpts[1] + ' (more compression)\n\n'\
        + 'B. Flat, slow anime (slice of life, everything is well-lit):\n\n'\
        + '   3. ' + encodeOpts[2] + '\n\n'\
        + 'C. Some dark scenes, some battle scenes (shonen, historical, etc.):\n\n'\
        + '   4. ' + encodeOpts[3] + ' (motion + fancy & detailed FX)\n'\
        + '   5. ' + encodeOpts[4] + ' (non-complex, motion only alternative)\n\n'\
        + 'D. Movie-tier dark scene, complex grain/detail, and BDs with dynamic-grain\n'\
        + '   injected debanding:\n\n'\
        + '   6. ' + encodeOpts[5] + '\n\n'\
        + 'E. I have infinite storage, a supercomputer, and I want details:\n\n'\
        + '   7. ' + encodeOpts[6] + '\n')
    
    for i in range(2): print("=" * 80)

    # get basic info from the user preset, incuding file types and episode naming ==
    # getNumber is (message, minvalue, maxvalue)
    
    preset = getNumber('\nPlease select [1-7]: ', 1, 7)

    SNUM = getNumber('\nPlease enter the season number: ', 0, 0)

    srcExt = getContainer("\nPlease specify input container (mkv, mp4, etc.): ")

    destExt = getContainer('\nPlease enter an output container: ')
    
    NUM = getNumber("\nPlease enter an episode to start at (affects naming only): ", 0, 0)
    
    #clean files before beginning work. This is necessary for mediainfo to behave correctly
    for file in os.listdir(os.getcwd()):
        if file.endswith(srcExt):
            os.rename(file, getValidFilenames(file))


    filename = ''
    for file in os.listdir(os.getcwd()):
        if file.endswith(srcExt):
            filename = file
            break
        else:
            continue
    # ==============================================================================

    command = 'mediainfo "--Output=Text;%ID%: %Format%$if(%Language/String%, SUBTITLE: '\
            + '.............. %Language/String% - %Title%)\\r\\n" ' + filename
    out = str(check_output(command)).replace("\\r", "").strip('b\'')
    out = clean(out)
    for i in range(len(out)):
        print(out[i])
    
    subindex = -1
    while subindex == -1:
        subindex = int(input('\nPlease enter an index for the subtitle '\
                   + 'track you wish to use (0 for no subs) [0-' + str(len(out)) + ']: '))
        if subindex > len(out) or subindex < 0:
            print("\nPlease input a valid value.")
            subindex = -1
        
    subtype = 0
    language = ''
    title = ''
    if subindex > 0:

        selection = out[subindex-1].split(" ")
        language = selection[4]
        title = " ".join(selection[6:])

        for i in range(len(out)):
            if out[i].find(language) !=-1:
                subindex = i + 1
                break

        if out[subindex-1].find('ASS') !=-1 or out[subindex-1].find('UTF-8') !=-1:
            subtype = 1
        elif out[subindex-1].find('PGS') !=-1:
            subtype = 2
        else:
            print('error')
    else:
        pass
    
    # == retrieve information from mediainfo and parse the output to show choices ==

    command = 'mediainfo "--Output=Audio;%ID%: [%Language/String%, ][%BitRate/String%, ]'\
            + '[%SamplingRate/String%, ][%BitDepth/String%, ][%^"Channel(s)/String"%, ]'\
            + '%Format%\\n" ' + filename
    out = str(check_output(command)).replace("\\r", "").strip('b\'')
    out = clean(out)
    print()
    for i in range(len(out)):
        print(out[i])
    
    audioindex = -1
    while audioindex == -1:
        audioindex = int(input('\nPlease enter an index for the audio '\
                   + 'track you wish to use: ')) - 1
        '''if audioindex > len(out)-1 or audioindex < 0:
            print("\nPlease input a valid value: ")
            audioindex = -1'''
    
    print("audioindex = " + str(audioindex))

    
    # ==============================================================================

    encode(srcDir, srcExt, encodeOpts[preset], language, title, audioindex, subindex, subtype, destDir, destExt, NUM, SNUM)

def encode(srcDir, srcExt, opts, language, title, audioindex, subindex, subtype, destDir, destExt, NUM, SNUM):
    OUTNAME = ''
    onemin = False
    test = str(input('1 min dummy encode? [Y]/n '))
    if test == 'Y' or test == 'y' or test == '':
        onemin = True
    for file in os.listdir(srcDir):
        if file.endswith('.'+srcExt):
            S = 'S' + str(SNUM).zfill(2) if SNUM < 10 else 'S' + str(SNUM)
            E = 'E' + str(NUM).zfill(2) if NUM < 10 else 'E' + str(NUM)
            OUTNAME = S + E
            if subindex > 0:
                subindex = checkSubs(file, language, title, subindex)[0]
                subtype = checkSubs(file, language, title, subindex)[1]
            if subtype == 1:
                subprocess.call(['ffmpeg', *(['-t', '00:01:00'] if onemin else []), '-i', file, \
                                    '-c:v', 'libx265', '-x265-params', opts, '-preset', 'slow', \
                                    '-vf', 'subtitles='+file+':stream_index='+str(subindex-1), \
                                    '-c:a', 'libopus', '-b:a', '96k', '-ac', '2', '-map', \
                                    '0:v:0', '-map', '0:a:'+str(audioindex), destDir + OUTNAME + '.' \
                                    + destExt])
                if onemin == True:
                    break
            elif subtype == 2:
                subprocess.call(['ffmpeg', *(['-t', '00:01:00'] if onemin else []), '-i', file, '-c:v', 'libx265', \
                                    '-x265-params', opts, '-preset', 'slow', '-filter_complex', \
                                    '[0:v][0:s:'+str(subindex-1)+']overlay[v]', '-map', '[v]', '-c:a', \
                                    'libopus', '-b:a', '96K', '-ac', '2', '-map', \
                                    '0:a:'+str(audioindex), destDir + OUTNAME + '.' + destExt])
                if onemin == True:
                    break
            else:
                subprocess.call(['ffmpeg', *(['-t', '00:01:00'] if onemin else []), '-i', file, \
                                    '-c:v', 'libx265', '-x265-params', opts, '-preset', 'slow', \
                                    '-c:a', 'libopus', '-b:a', '96K', '-ac', '2', '-map', '0:v', \
                                    '-map', '0:a:'+str(audioindex), destDir + OUTNAME + '.' + destExt])
                if onemin == True:
                    break
            NUM +=1
        
def clean(out):
    out = out.split('\\n')
    for i in range(len(out)):
        if out[len(out)-1] == '':
            out.pop(len(out)-1)
    for i in range(len(out)):
        out[i] = re.sub(r'^.*? ', '', out[i])
        out[i] = str(i + 1) + '. ' + out[i]
    return out

def getNumber(message, min, max):
    while True:
        try:
            NUM  = int(input(message))
            if NUM < min:
                print('\nMust be at least ' + str(min) + '. Try again.')
                continue
            if max != 0 and NUM > max:
                print("\nValue too large. Try again.")
                continue
            else:
                return NUM
        except ValueError:
            print("Null input or not an integer! Try again.")
            continue

def checkSubs(filename, language, title, subindex):
    command = 'mediainfo "--Output=Text;%ID%: %Format%$if(%Language/String%, SUBTITLE: '\
            + '.............. %Language/String% - %Title%)\\r\\n" ' + filename
    out = str(check_output(command)).replace("\\r", "").strip('b\'')
    out = clean(out)
    
    subindex = 0

    """to be updated in the future - this essentially prefers the title of the subs over the
    language to ensure that regardless of the index of the subs, the most optimal subtitle
    track is chosen based on the initial chosen index"""

    subtype = 0
     
    for i in range(len(out)):
        if out[i].find(language) !=-1:
            subindex = i + 1
            break

    for i in range(len(out)):
        if out[i].find(title) !=-1:
            subindex = i + 1
            break
    else:
        pass

    if out[subindex-1].find('ASS') !=-1 or out[subindex-1].find('UTF-8') !=-1:
        subtype = 1
    elif out[subindex-1].find('PGS') !=-1:
        subtype = 2
    else:
        print('error')

    return subindex, subtype


def getContainer(message):
    valCont = ['mkv', 'mp4', 'mov', 'avi', 'webm', 'mpg', 'wmv', 'm4v', 'm2ts']
    while True:
        cont = input(message)
        if cont in valCont:
            return cont
        else:
            print("\nInvalid. Supported containers are: ")
            for i in range(len(valCont)): print(valCont[i])
            continue

def getValidFilenames(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

if __name__ == "__main__":
    main()