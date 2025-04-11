import exifread
import os
import shutil
 
# Set the directory you want to start from
rootDir = '.'
for dirName, subdirList, fileList in os.walk(rootDir):
	list=[]
	if os.path.split(dirName)[1][0:2]=="20":
		continue
	print dirName
	for fname in fileList:
		ext=os.path.splitext(fname)[1]
		if (ext==".jpg" or ext==".JPG" or ext==".jpeg" or ext==".JPEG"):
			oriPath=os.path.join(dirName,fname)
			f=open(oriPath,'rb')
			tags=exifread.process_file(f)
			f.close()
			if "EXIF DateTimeOriginal" in tags.keys():
				date=str(tags["EXIF DateTimeOriginal"])
				#print date[0:4]+'-'+date[5:7]+'-'+date[6:8]
				list.append(date[0:4]+'-'+date[5:7]+'-'+date[8:10])
	sort=sorted(list)
	if len(sort)>0:
		os.rename(os.path.split(dirName)[1],sort[0]+" "+os.path.split(dirName)[1])
		print "renamed to "+sort[0]+" "+os.path.split(dirName)[1]+"\n"
