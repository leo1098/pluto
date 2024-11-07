# pluto

Command-line tool to automate some Web-App Penetration Test phases. 

## Requirements

- chromedriver. Download from https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json and place it in an executable path. Place that path in the `chrome_driver_path` variable in `csp.py`. It has to match the main version of the installed Chrome or Chromium.

If something breaks, download chromium and chromiumwebdirver from here:

https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux_x64/

## TODO

- [DONE] Update fetch csp function so that it does that manually. Targets might not be reachable by Google's tool
- [DONE] fix report title with website one
- [] Add `httpx` support
- [] Add `nmap` support
- [] Add `nikto` support
