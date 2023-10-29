#!/usr/bin/env bash
# https://gist.github.com/nhtua/2d294f276dc1e110a7ac14d69c37904f

# check if ANDROID_HOME env is set
[ -z ${ANDROID_HOME} ] && android_home='android_sdk' || android_home="${ANDROID_HOME}";
echo "found ANDROID_HOME=$ANDROID_HOME"

# get arguments
while [ $# -gt 0 ] ; do
        case $1 in
                --android_version)
                        android_version="$2"
                        shift
                        shift
                        ;;
                --android_home)
                        android_home="$2"
                        shift
                        shift
                        echo "force android_home=$android_home"
                        ;;
                -n|--name)
                        name="$2"
                        shift
                        shift
                        ;;
                --force)
                        force="$1"
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

if [[ -z "$android_version" ]]; then
        android_version="31"
fi

if [[ -z "$name" ]]; then
        name=android_$android_version
fi

# get realpath if path relative
android_home=$(realpath $android_home)

yes | $android_home/cmdline-tools/latest/bin/sdkmanager --sdk_root=$android_home --install "platforms;android-$android_version" "emulator"

case "$(uname -m)" in
   arm64*)
     system_image="system-images;android-$android_version;google_apis_playstore;arm64-v8a"
     ;;
   x86_64*)
     system_image="system-images;android-$android_version;google_apis_playstore;x86_64"
     ;;
esac

yes | $android_home/cmdline-tools/latest/bin/sdkmanager --sdk_root=$android_home --install $system_image
echo no | $android_home/cmdline-tools/latest/bin/avdmanager create avd -n $name -k $system_image $force

echo ""
echo "______________________________________________"
if [[ ! ":$PATH:" == *":$android_home/emulator"* ]]; then
        echo "Please export following environment variables:"
        echo "export PATH="\$PATH:$android_home/emulator""
        echo "______________________________________________"
fi
echo "___________________________________"
echo "Please make sure that the DISPLAY variable is set properly before starting the AVD."
echo "start your avd with:"
echo "./start_avd.sh --name $name"