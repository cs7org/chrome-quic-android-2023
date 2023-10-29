#!/usr/bin/env bash
# https://gist.github.com/nhtua/2d294f276dc1e110a7ac14d69c37904f

set -e

echo "__________________________________________"
# check if ANDROID_HOME env is set
[ -z ${ANDROID_HOME} ] && android_home='android_sdk' || android_home="${ANDROID_HOME}"; echo "found ANDROID_HOME=$ANDROID_HOME"

# get arguments
while [ $# -gt 0 ] ; do
        case $1 in
                -n|--name)
                        name="$2"
                        shift
                        shift
                        ;;
                --android_home)
                        android_home="$2"
                        shift
                        shift
                        echo "force android_home=$android_home"
                        ;;
                --headless)
                        headless="-no-window"
                        shift
                        ;;
                -*|--*)
                        echo "Unknown option $1"
                        exit 1
                        ;;
                *)
                        POSITIONAL_ARGS+=("$1") # save positional arg
                        shift # past argument
                        ;;
        esac
done

if [[ -z "$name" ]]; then
        name="android_31"
fi

# get realpath if path relative
android_home=$(realpath $android_home)

echo "__________________________________________"
if ! command -v $android_home/emulator/emulator &> /dev/null; then
        echo "ERROR can't find emulator binary"
        echo "use ./create_avd.sh --name $name"
fi

if ! emulator -list-avds | grep -q "$name"; then
        echo "ERROR can't find avd with the name $name"
        echo "__________________________________________"
        echo "following avds are available:"
        emulator -list-avds
        echo "__________________________________________"
        echo "otherwise create a new one:"
        echo "./create_avd.sh --name $name"
        exit
fi

if screen -list | grep -q "$name"; then
    echo "emulator running already"
    exit
fi

# problems with Ubuntu 22.03.4 (Joerg 10/2023)
# https://stackoverflow.com/questions/75559010/android-emulator-freezing-on-ubuntu
# https://stackoverflow.com/questions/62690044/android-emulator-control-buttons-back-home-recent-are-not-working
$android_home/emulator/emulator -feature -Vulkan -avd $name -no-audio -verbose $headless
