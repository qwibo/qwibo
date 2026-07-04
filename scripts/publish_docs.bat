@echo off
REM Publish MkDocs to qwibo.github.io/docs (same Pages-repo flow).
REM Prerequisite: clone qwibo.github.io next to this repo.
REM Usage: scripts\publish_docs.bat   then git push in the Pages repo.
cd /d "%~dp0\.."
python scripts\publish_docs.py
exit /b %ERRORLEVEL%
