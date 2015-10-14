@echo off
set current_dir=%~dp0\..\Web\TaobaoShop
pushd %current_dir%

python.exe index.py

popd
