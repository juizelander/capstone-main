#!/bin/bash
git status > git_status.txt
git reset --soft origin/stizzzy
git add capstone/settings.py
git commit -m "feat: implement chatbot fallback, fix application bugs"
git status >> git_status.txt
