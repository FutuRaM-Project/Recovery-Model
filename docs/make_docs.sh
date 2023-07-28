#! bin/bash

git checkout main
cp -r docs/_build /tmp/_build
git checkout gh-pages
cp -r /tmp/_build .
git add .
git commit -m "update docs"
git checkout main
