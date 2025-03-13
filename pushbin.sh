#!/bin/sh

scripts=("curls.sh" "ffbili.py" "ffconcat.sh" "ffmp3.sh")
destpath="${HOME}/bin"

for script in "${scripts[@]}";
do
    echo "${script} ..."
    if [[ ! -f "${destpath}/${script}" ]]; then
        cp ${script} ${destpath} && chmod +x ${destpath}/${script}
        echo "copy ok"
    else
        cmp -s ${script} ${destpath}/${script} && echo "pass" && continue
        cp -f ${script} ${destpath} && chmod +x ${destpath}/${script}
        echo "overwrite ok"
    fi
done

