## Environment Setup

Create virtual environment

python -m venv env

Activate environment

Windows
env\Scripts\activate

Install dependencies

pip install -r requirements.txt

## How Others Will Run Your Project

Anyone can reproduce your environment using:

git clone <repo>

cd youtube_downloader

python -m venv env

env\Scripts\activate

pip install -r requirements.txt

## Next Steps (Push to Git)

Run:

git init
git add .
git commit -m "Initial YouTube downloader & history parser project"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main

## Git Regular Commits
git status
git add .
git commit -m "Initial YouTube downloader & history parser project"
git push -u origin main