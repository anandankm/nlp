#!/bin/bash
# Author: Anandan Rangasmay andy.compeer@gmail.com
#                           andy@grooveshark.com
line_numbers=$(grep -n resumption corpus.en | awk -F":" 'BEGIN{s=""}{s=s" "$1}END{print s}')
sh_file="resumption_foreign_sh"
py_file="resumption_foreign_py"
for i in $line_numbers
do 
    head -$i corpus.es | tail -1
done |
awk '{for(i=1;i<=NF;i++){s[$i]=0;}}END{for(i in s){print i;}}' > $sh_file 
sort $sh_file > ${sh_file}"_"
sort $py_file > ${py_file}"_"
mv ${sh_file}"_" $sh_file 
mv ${py_file}"_" $py_file 
if [ -z $(diff $py_file $sh_file) ]
then
    echo "Files match. Check passed."
else
    echo "Files do not match. Check did not pass!!"
fi
