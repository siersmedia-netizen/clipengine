# ClipEngine Setup Guide
### Zero PC needed after this. Everything runs in the cloud.

---

## Files you need (all included)
- clipengine.py
- requirements.txt
- nixpacks.toml
- streams.txt

---

## STEP 1 — Make a GitHub account
1. Go to **github.com**
2. Click Sign Up — it's free
3. Make your account

---

## STEP 2 — Upload your files to GitHub
1. Once logged in, click the **+** button top right
2. Click **New repository**
3. Name it: `clipengine`
4. Make sure it says **Private**
5. Click **Create repository**
6. Click **uploading an existing file**
7. Drag ALL 4 files into the box
8. Click **Commit changes**

---

## STEP 3 — Make a Railway account
1. Go to **railway.app**
2. Click **Login with GitHub**
3. Approve the connection

---

## STEP 4 — Deploy on Railway
1. Click **New Project**
2. Click **Deploy from GitHub repo**
3. Select your **clipengine** repo
4. Railway sets up automatically

---

## STEP 5 — Add your Instagram info
1. In Railway click your project
2. Click **Variables** on the left
3. Add these one by one:

IG_USERNAME = wspsiers
IG_PASSWORD = your Instagram password
STREAMER_NAME = Neon
CLIPS_PER_DAY = 20
DELAY_MINUTES = 15

---

## STEP 6 — Add stream links
1. Go to your GitHub repo
2. Click streams.txt
3. Click the pencil to edit
4. Paste YouTube links one per line:

https://youtube.com/watch?v=XXXXXXXXXXX
https://youtube.com/watch?v=YYYYYYYYYY

5. Click Commit changes
6. Railway restarts automatically and starts working

---

## Done. Your PC can be off forever.

To add more streams later just edit streams.txt on GitHub from your phone.

---

## IMPORTANT
Turn off Instagram two-factor authentication before running or the login will fail.
