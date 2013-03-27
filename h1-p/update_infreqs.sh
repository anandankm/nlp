 #!/bin/bash
awk -F" " '
BEGIN {
    while(getline line < "gene.tag.counts") {
        split(line, s," ");
        if(s[1]<5) {
            a[s[4]]=1;
        }
    }
}
{
    if(a[$1] != "") {
        print $1" _RARE_"
    } else {
        print $0 
    }
}
' gene.train > gene.p1.sh.train
