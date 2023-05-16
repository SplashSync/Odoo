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
# Import Docker Image to Gitlab Registry
################################################################################

function import_image() {
    name="$1"
    key="$2"

    subtitle "Import Docker Image to Registry: $name"
    docker pull $name
    docker image tag $name $CI_REGISTRY_IMAGE:$key
    docker push $CI_REGISTRY_IMAGE:$key
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