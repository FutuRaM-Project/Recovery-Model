#! bin/bash

sphinx-apidoc -fo ../src/ .

make html
