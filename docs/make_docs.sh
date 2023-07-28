#! bin/bash

git checkout main
cp -r _build /tmp/_build
git checkout gh-pages
cp -r /tmp/_build/ .
git add .
git commit -m "update docs"

