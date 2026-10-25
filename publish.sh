#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ -x .env/bin/python ] && .env/bin/python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    . .env/bin/activate
    pip show twine >/dev/null 2>&1 || pip install --upgrade pip setuptools wheel twine
else
    if [ -d .env ]; then
        echo "[$(date)] Existing .env is not Python 3.10+; recreating it."
        rm -rf .env
    else
        echo "[$(date)] Creating virtualenv."
    fi
    python3 -m venv .env
    . .env/bin/activate
    pip install --upgrade pip setuptools wheel twine
fi

VERSION=$(python setup.py --version 2>/dev/null | tail -1)
echo "[$(date)] Building proxytypes3 $VERSION (sdist + wheel)."
rm -rf dist
python setup.py sdist bdist_wheel

echo "[$(date)] Built:"
ls -1 dist

if grep -qs '^\[proxytypes3\]' ~/.pypirc; then
    REPO="--repository proxytypes3"
    echo "[$(date)] Uploading to the proxytypes3 .pypirc repository."
else
    REPO=""
    echo "[$(date)] Uploading to PyPI (no [proxytypes3] .pypirc section found)."
fi
twine upload $REPO dist/proxytypes3-$VERSION*