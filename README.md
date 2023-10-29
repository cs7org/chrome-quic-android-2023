# Load h2 and h3 websites via automated (Android) Chrome
 * 2023-02-15, Matthias: Final version for project thesis, tested with MacOS and Linux and Chrome v109.
 * 2023-10-28, Joerg: Tested with Ubuntu 22.04.3 LTS and Chrome v118. MacOS *not* tested.

## Prepare Android Virtual Device (AVD) and Android Debug Bridge (ADB)
```
sudo apt install git curl openjdk-19-jre python3-pip
python3 -m pip install pandas validators selenium seaborn

./install_adb.sh
# export environment variables as shown in output

./create_avd.sh --name android_31
# export environment variables as shown in output

./start_avd.sh --name android_31
# install chrome v118 via play store (or via update)

# avd can also be started with the --headless argument (./start_avd.sh --name android_31 --headless)
```

## Run experiments
See `quicbench.py` (set `--android` flag if you want to use Android)
