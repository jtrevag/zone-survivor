#!/bin/bash
# Run this from the stalker-survivor directory after creating your GitHub repo

git init
git add .
git commit -m "docs: initial design documentation"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
