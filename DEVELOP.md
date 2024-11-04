
# Tech Stack

- python3
- html/css/js
- fastapi
- vue
- element-ui


# Build
```
pip3 install poetry

git clone git@github.com:codematrixer/ui-viewer.git
cd ui-viewer

poetry lock --no-update
poetry install
poetry build
```

# Run
```
poetry run python3 -m uiviewer
```