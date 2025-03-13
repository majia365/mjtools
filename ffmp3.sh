#!/bin/sh

# 使用ffmpeg从视频mp4文件中抽取音频mp3
#输入参数1: 输出音质

#命令行帮助
print_usage() {
    echo "usage: ffmp3.sh [quality]"
    echo "    quality: best/high/medium/low/fm/am"
    exit
}

#音乐音质参数
best_quality="-ar 48000 -ac 2 -q:a 0"
high_quality="-ar 44100 -ac 2 -b:a 320k"
medium_quality="-ar 44100 -ac 2 -b:a 192k"
low_quality="-ar 44100 -ac 2 -b:a 128k"
#广播音质参数
fm_quality="-ar 22050 -ac 1"
am_quality="-ar 11025 -ac 1"

default_quality=${best_quality}

#检查命令行参数
if [[ $# -eq 0 ]]; then
	quality=${default_quality}
elif [[ $# -eq 1 ]]; then
    if [[ ${1} == "best" ]]; then
    	quality=${best_quality}
    elif [[ ${1} == "high" ]]; then
    	quality=${high_quality}
    elif [[ ${1} == "medium" ]]; then
    	quality=${medium_quality}
    elif [[ ${1} == "low" ]]; then
    	quality=${low_quality}
    elif [[ ${1} == "fm" ]]; then
    	quality=${fm_quality}
    elif [[ ${1} == "am" ]]; then
    	quality=${am_quality}
    else
    	print_usage
    fi
else
    print_usage
fi

#处理.mp4生成.mp3
for file in *.mp4;
do
	if [[ "${file}" = "*.mp4" ]]; then
		echo "Not Found mp4."
		break
	fi
	echo "${file} ..."
	if [[ ! -f "${file%.mp4}.mp3" ]]; then
		ffmpeg -loglevel error -i "${file}" -map_metadata -1 -vn ${quality} "${file%.mp4}.mp3"
	else
		echo "pass"
	fi
done

