 #!/bin/bash
awk -F" " '
BEGIN {
    while(getline line < "gene.tag.counts") {
        split(line, s," ");
        if(s[1]<5) {
            a[s[3]" "s[4]]=1;
        }
    }
}
{
    if(a[$2" "$1] == 1) {
        print "_RARE_ "$2
    } else {
        print $0 
    }
}
' gene.train > gene.p1.sh.train
