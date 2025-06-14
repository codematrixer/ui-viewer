# ui-viewer
[![github actions](https://github.com/codematrixer/ui-viewer/actions/workflows/release.yml/badge.svg)](https://github.com/codematrixer/ui-viewer/actions)
[![pypi version](https://img.shields.io/pypi/v/uiviewer.svg)](https://pypi.python.org/pypi/uiviewer)
![python](https://img.shields.io/pypi/pyversions/uiviewer.svg)

UI hierarchy inspector for Mobile App, supporting `Android`, `iOS`, and `HarmonyOS NEXT`. 

Its features include:

- visualize the UI hierarchy via screenshot and tree structure.
- view element properties
- auto generate XPath or XPathLite
- auto generate coordinate percentages.
- and more…


This project is developed using FastAPI and Vue. It starts locally and displays UI hierarchy through web browser.

![show](https://github.com/user-attachments/assets/cd277443-2064-4c98-a5c9-214ee6fae674)

# Installation
- python3.8+

```shell
pip3 install -U uiviewer
```

# Run
Run the following command on the terminal. (default port `8000`)

```shell
uiviewer
# or
python3 -m uiviewer

INFO:     Started server process [46814]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:55080 - "GET / HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:55080 - "GET /static/index.html HTTP/1.1" 200 OK
INFO:     127.0.0.1:55080 - "GET /static/css/style.css HTTP/1.1" 200 OK
INFO:     127.0.0.1:55080 - "GET /static/js/index.js HTTP/1.1" 200 OK
INFO:     127.0.0.1:55080 - "GET /static/js/api.js HTTP/1.1" 200 OK
INFO:     127.0.0.1:55082 - "GET /static/js/utils.js HTTP/1.1" 200 OK
INFO:     127.0.0.1:55082 - "GET /static/js/config.js HTTP/1.1" 200 OK
INFO:     127.0.0.1:55082 - "GET /version HTTP/1.1" 200 OK
```
And then open the browser to [http://localhost:8000](http://localhost:8000)

You can also customize port to start the service.
```shell
uiviewer -p <PORT>
# or
python3 -m uiviewer -p <PORT>

```

# Environment
If you need to connect to a remote HDC Server or ADB server for remote device debugging, you must set the required environment variables before starting uiviewer.

HarmonyOS
```bash
export HDC_SERVER_HOST=127.0.0.1  # Replace with the remote host
export HDC_SERVER_PORT=8710
```

Android
```bash
export ANDROID_ADB_SERVER_HOST=127.0.0.1  # Replace with the remote host
export ANDROID_ADB_SERVER_PORT=5037
```

If you want to remove Environment Variables, To unset the environment variables:
```bash
unset HDC_SERVER_HOST
unset HDC_SERVER_PORT

unset ANDROID_ADB_SERVER_HOST
unset ANDROID_ADB_SERVER_PORT
```


# Tips
- If you are using a virtual environment, please make sure to activate it before running the command.

- On iOS, please ensure that WDA is successfully started and wda port forwarding is successful in advance.
  -   First, Use `xcode` or  `tidevice` or `go-ios` to launch wda.
  ```
  tidevice xctest -B <wda_bundle_id>
  ```
  - Second, Use `tidevice` or `iproxy` to forward the wda port，and keep it running.
  ```
  tidevice relay 8100 8100
  ```
  - And then, To ensure the success of the browser to access `http://localhost:8100/status`, return like this:
  ```
  {
    "value": {
        "build": {
            "productBundleIdentifier": "com.facebook.WebDriverAgentRunner",
            "time": "Mar 25 2024 15:17:30"
        },
        ...
        "state": "success",
        "ready": true
    },
    "sessionId": null
  } 
  ```
  - Finally, Input the **`wdaUrl`** in the web page, such as `http://localhost:8100`

- On iOS，WDA can easily freeze when dumping high UI hierarchy. You can reduce the **`maxDepth`** on the web page. The default is 30.


# Relevant
- https://github.com/codematrixer/hmdriver2
- https://github.com/openatx/uiautomator2
- https://github.com/openatx/facebook-wda
- https://github.com/alibaba/web-editor
