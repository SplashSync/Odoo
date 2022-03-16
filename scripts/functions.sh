#!/bin/sh
################################################################################
#
# * This file is part of Immo-Pop Website Project.
# *
# * Copyright (C) Immo-Pop SAS <www.immo-pop.com>
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# *
# * For the full copyright and license information, please view the LICENSE
# * file that was distributed with this source code.
#
################################################################################

################################################################
# Define Layout Colors
bash_layout="0;1;97;41;5;26m"
bash_layout_splash="0;1;97;41;5;26m"

################################################################
# Render Titles
title () {
  printf "\033[%s %-50s \033[0m \n" $bash_layout ""
  printf "\033[%s %-50s \033[0m \n" $bash_layout "$@"
  printf "\033[%s %-50s \033[0m \n" $bash_layout ""
}

################################################################
# Render Subtitles
subtitle () {
  printf "\033[%s %-50s \033[0m \n" $bash_layout "$@"
}

################################################################
# Render Splash Screen
splashscreen () {
  printf "\033[%s %-50s \033[0m \n" $bash_layout_splash "=================================================="
  printf "\033[%s == %-44s == \033[0m \n" $bash_layout_splash "$@"
  printf "\033[%s %-50s \033[0m \n" $bash_layout_splash "=================================================="
}

################################################################################
# Load Docker Images from Cache or Registry
################################################################################

function import_image() {
    name="$1"
    md5=$(echo -n $name | md5sum | awk '{print $1}')
    if [ -f "images/$md5.tar" ]; then
        subtitle "Load Docker Image from Cache: $name"
        cat "images/$md5.tar" | docker import - $name
    else
        subtitle "Load Docker Image from Registry: $name"
        docker pull postgres:10
        subtitle "Save Docker Image to Cache: $name"
        mkdir -p "images"
        docker save -o "images/$md5.tar" $name
    fi
    docker image ls
}

################################################################
# Composer Update (Optional)
if [ "$1" = "--demo" ];
then
    echo "\n"
    splashscreen "    !/!   THIS is a SPLASH Screen  !/!      "
    echo "\n"
    title "THIS is a TITLE"
    echo "\n"
    subtitle "THIS is a SUB TITLE"
    echo "\n"
fi