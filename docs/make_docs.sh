#! bin/bash
ghpush update-docs
git checkout main
cp -r docs/_build ~/tmp
git checkout gh-pages
cp -r ~/tmp/_build/* .
git add .
git commit -m "update docs"
git push
#git checkout main
