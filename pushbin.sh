#!/bin/sh

scripts=("ffbili.py" "ffconcat.sh" "ffmp3.sh")

for script in "${scripts[@]}"
do
  echo ${script} "..."
  cp -f ${script} ~/bin && chmod +x ~/bin/${script}
done

