#! bin/bash

ghpush update-docs
git checkout main
cp -R docs/_build/html ~/tmp/futuram-ghpages
git checkout gh-pages
cp -R ~/tmp/futuram-ghpages/html/* .
git add .
git commit -m "update docs"
git push
#git checkout main
