#!/bin/bash

set -xe

git clone --depth 1 -b v3.0.0 https://github.com/ryanoasis/nerd-fonts.git
cd nerd-fonts
git apply < ../font-patcher.patch
cd ..

curl -O http://ftp.jaist.ac.jp/pub/pkgsrc/distfiles/inconsolata-ttf-2.001/Inconsolata-Bold.ttf
curl -O http://ftp.jaist.ac.jp/pub/pkgsrc/distfiles/inconsolata-ttf-2.001/Inconsolata-Regular.ttf
curl -L -O https://osdn.net/downloads/users/25/25473/NasuFont-20200227.zip
unzip NasuFont-20200227.zip

curl -O https://raw.githubusercontent.com/chuyii/mig-mono/master/replaceparts_generator.py
patch -p1 < replaceparts_generator.patch
python replaceparts_generator.py
