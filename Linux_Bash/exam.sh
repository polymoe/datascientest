#!/bin/bash

cartes=(rtx3060 rtx3070 rtx3080 rtx3090 rx6700)

function print_in_file {
echo "$1:$2" >> ~/exam_TOUMI/sales.txt
}

echo `date` >> ~/exam_TOUMI/sales.txt 


for carte in ${cartes[*]}
do
lien="http://0.0.0.0:5000/$carte"
nombre=`curl $lien`
print_in_file $carte $nombre
done
