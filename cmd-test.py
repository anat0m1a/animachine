import subprocess
import shlex
import os
import re
from pymediainfo import MediaInfo

srcDir = '/Users/lizzy/Movies/Sailor_Moon/'
destDir = '/Users/lizzy/Movies/Sailor_Moon/Converted/'

srcExt = 'mkv'
print("testing cmd...")

def getValidFilenames(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

cmd = shlex.split("which mediainfo")

print(subprocess.Popen(["which", "mediainfo"]))


# Clean files before beginning work. This is necessary for mediainfo to behave correctly
for file in os.listdir(srcDir):
    if file.endswith(srcExt):
        os.rename(srcDir + file, srcDir + getValidFilenames(file))

filename = ''
for file in os.listdir(srcDir):
    if file.endswith(srcExt):
        filename = file
        break
    else:
        continue

media_info = MediaInfo.parse(srcDir + filename)
media_info = MediaInfo.to_data(media_info)

tempList = []

for tempTrack in media_info['tracks']:
    if tempTrack['track_type'] == 'Audio':
        tempList.append(tempTrack) 
        print(f"""{len(tempList)}) Language: {tempTrack['language']}
Framerate: {tempTrack['frame_rate']}""")
        print("test")