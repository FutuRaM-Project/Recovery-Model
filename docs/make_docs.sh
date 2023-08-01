#! bin/bash
venv futuram-dev
cd ~/code/gh/futuram/IntegratedModel
cd docs
make html
cd ..

cp -R * ../FutuRaM-Model-Docs/
cd ../FutuRaM-Model-Docs/docs
make html

git add .
git commit -m update-docs
git push

cd ~/code/gh/futuram/IntegratedModel
