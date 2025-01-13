#!/bin/sh

#音乐音质
best_quality="-ar 44100 -ac 2 -q:a 0"
low_quality="-ar 44100 -ac 2 -b:a 128k"
medium_quality="-ar 44100 -ac 2 -b:a 192k"
high_quality="-ar 44100 -ac 2 -b:a 320k"
#广播音质
am_quality="-ar 11025 -ac 1"
fm_quality="-ar 22050 -ac 1"

#命令行帮助
print_usage() {
    echo "usage: ffmp3.sh [quality]"
    echo "\t quality: best/low/medium/high/am/fm"
    exit
}

#检查命令行参数
if [[ $# -eq 0 ]];
then
	quality=${best_quality}
elif [[ $# -eq 1 ]];
then
    if [[ ${1} == "best" ]]; then
    	quality=${best_quality}
    elif [[ ${1} == "low" ]]; then
    	quality=${low_quality}
    elif [[ ${1} == "medium" ]]; then
    	quality=${medium_quality}
    elif [[ ${1} == "high" ]]; then
    	quality=${high_quality}
    elif [[ ${1} == "am" ]]; then
    	quality=${am_quality}
    elif [[ ${1} == "fm" ]]; then
    	quality=${fm_quality}
    else
    	print_usage
    fi
else
    print_usage
fi

#处理.mp4生成.mp3
for file in *.mp4;
do
	if [ "${file}" = "*.mp4" ]
	then
		break
	fi
	echo "${file}"
	if [ ! -f "${file%.mp4}.mp3" ]
	then
		ffmpeg -loglevel error -i "${file}" -map_metadata -1 -vn ${quality} "${file%.mp4}.mp3"
	else
		echo "pass"
	fi
done


