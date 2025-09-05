  
#!/bin/bash

# Exit in case of error
set -e

if [ ! -d ./fastapi-react-mamba ] ; then
    echo "Run this script from outside the project, to generate a sibling dev project"
    exit 1
fi

rm -rf ./dev-fastapi-react-mamba

cookiecutter --no-input -f ./fastapi-react-mamba project_slug="dev-fastapi-react-mamba"