#!/usr/bin/env bash
# https://gist.github.com/nhtua/2d294f276dc1e110a7ac14d69c37904f

set -e

# check if ANDROID_HOME env is set
[ -z ${ANDROID_HOME} ] && android_home='android_sdk' || android_home="${ANDROID_HOME}"

# get arguments
while [[ $# -gt 0 ]] ; do
        case $1 in
                --android_home)
                  android_home="$2"
                  echo "forcing ANDROID_HOME=$android_home"
                  shift
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

# get realpath if path relative
android_home=$(realpath $android_home)

# download sdkmanager if not exists, otherwise use sdkmanager
if ! command -v sdkmanager &> /dev/null
then
    rm -rf cmdline-tools
    case "$(uname -s)" in
       Darwin*)
         clt_url="https://dl.google.com/android/repository/commandlinetools-mac-9123335_latest.zip"
         ;;
       Linux*)
         clt_url="https://dl.google.com/android/repository/commandlinetools-linux-9123335_latest.zip"
         ;;
    esac
    echo "download commandlinetools.zip: $clt_url"
    curl -o commandlinetools.zip $clt_url

    unzip commandlinetools.zip
    rm commandlinetools.zip

    sdkmanager=$(realpath "./cmdline-tools/bin/sdkmanager")
else
    sdkmanager="sdkmanager"
fi

mkdir -p $android_home
yes | $sdkmanager --sdk_root=$android_home --install "platform-tools" "cmdline-tools;latest"

# remove cmdline-tools if exists
rm -rf cmdline-tools

# https://developer.android.com/studio/command-line
# We recommend setting the environment variable for ANDROID_HOME when using the command line. Also, set your command search path to include ANDROID_HOME/tools, ANDROID_HOME/tools/bin, and ANDROID_HOME/platform-tools to find the most common tools. The steps vary depending on your OS, but read How to set environment variables for general guidance
echo "Please set following environment variables:"
# TODO ANDROID_SDK_HOME for emulator?
echo "export ANDROID_SDK_HOME=$android_home"
echo "export ANDROID_HOME=$android_home"
echo "export PATH=\$PATH:$android_home/cmdline-tools/latest:$android_home/cmdline-tools/latest/bin:$android_home/platform-tools"