#!/bin/sh

#如果命令行参数没有提供文件名模版，退出
if [ $# -eq 0 ]
then
	echo "miss template"
	exit 0
fi

#命令行参数即为模版，多个参数为多模版
overwrite="-y"
tempno=0
for template in $@;
do
	if [[ ${template} == "-y" ]];
	then
		overwrite="-y"
		continue
	fi
	tempno=$((tempno+1))
	echo "template${tempno}: ${template}"
	#检查是否有匹配文件，没有匹配文件则跳出本次循环
    ls ${template}*.mp4 &> /dev/null
    if [[ $? -ne 0 ]];
    then
    	echo "No such file."
    	continue
    fi
	#第一步，找出符合该模版的文件中排序用的字段数
	n=0
	for file in `ls -l -1 ${template}*.mp4`;
	do
		#将文件名用"."拆分成字段数组
		var_arr=(`echo ${file} | tr '.' ' '`)
		for var in ${var_arr[@]};
		do
			n=$((n+1))
			#找到"p*"格式字段，即为排序字段，跳出循环
			if [[ ${var} =~ ^p([0-9]*)$ ]]
			then
				break 2
			fi
		done
	done
	#使用排序字段里的数字进行ls排序，写入source.lst文件
	listfile="source${tempno}.lst"
	seq=0
	for file in `ls -l -1 ${template}*.mp4 | sort -t "." -k${n}.2n`;
	do
		seq=$((seq+1))
		echo "${file}"
		if [ ${seq} -eq 1 ]
		then
			echo "file '${file}'" > ${listfile}
		else
			echo "file '${file}'" >> ${listfile}
		fi
	done
	#如果找到了匹配文件，则执行ffmpeg concat
	if [[ ${seq} -gt 0 ]];
	then
		#执行ffmpeg concat
		cmdline="ffmpeg -loglevel error -f concat -safe 0 -i ${listfile} -codec copy -movflags faststart ${overwrite} output_whole${tempno}.mp4"
		echo ${cmdline}
		${cmdline}
	fi
done
