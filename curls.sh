#!/bin/sh

# 使用curl进行批量下载

#命令行帮助
print_usage() {
    echo "usage: curls.sh <url>"
    echo "    [001-020] 连续编号下载"
    echo "    {001,020} 指定编号下载"
    exit
}

#检查命令行参数
if [[ $# -ne 1 ]]; then
    print_usage
fi

if [[ "${1}" =~ ^(http|https)://.*$ ]]; then
    url=${1}
else
    print_usage
fi

#curl参数设置
browser=( \
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0" \
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15" \
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.205 Safari/537.36" \
)
num=${#browser[@]}
ct=10  #connect-timeout
mt=60  #max-time
parallel=""  #--parallel --parallel-immediate
retry="--retry 10 --retry-delay 1 --retry-max-time 10"
while ((1)); do
    echo ${url}
    rnd=$(( RANDOM % num ))
    curl --user-agent "${browser[rnd]}" --connect-timeout ${ct} --max-time ${mt} ${parallel} ${retry} -C - -L -O "${url}" && break
    sleep 1
    ct=$((ct+rnd))
    mt=$((mt+rnd))
done

