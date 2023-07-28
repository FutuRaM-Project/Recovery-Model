#! bin/bash

git checkout main
cp -r docs/_build/* ~/tmp
git checkout gh-pages
cp -r ~/tmp/* .
git add .
git commit -m "update docs"
git push
git checkout main
