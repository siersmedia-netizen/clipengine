#!/usr/bin/env python3
"""
ClipEngine — Auto Clip & Post to Instagram
For: Neon clipping page (@wspsiers)
Runs on Railway.app 24/7 — no PC needed
"""

import os
import json
import time
import random
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
#  EASY SETUP — CHANGE THESE
# ============================================================
INSTAGRAM_USERNAME = "wspsiers"       # Your Instagram username
INSTAGRAM_PASSWORD = "YOUR_PASSWORD_HERE"  # Your Instagram password
CLIPS_PER_DAY = 20                    # How many to post per day
DELAY_BETWEEN_POSTS = 900             # Seconds between posts (15 min default)
STREAMER_NAME = "Neon"               # Streamer name for captions
# ============================================================

STREAMS_FILE = "streams.txt"          # Add YouTube links here, one per line
POSTED_FILE = "posted_clips.json"     # Tracks what's been posted
CLIPS_DIR = Path("clips")             # Where clips are saved
CLIPS_DIR.mkdir(exist_ok=True)

# Hashtags used by top clipping pages
HASHTAGS = (
    "#neon #neonstreamer #twitch #twitchclips #twitchhighlights "
    "#streamhighlights #gaming #gamingclips #viralclips #fyp "
    "#foryou #foryoupage #gamingmoments #clutch #highlights "
    "#streamclips #gamingreels #twitchmoments #viral #explore"
)

# Caption templates that drive comments
CAPTION_TEMPLATES = [
    "this {streamer} clip is INSANE 😭🔥 comment what you think happened next 👇",
    "bro {streamer} really said that 💀💀 drop a 🔥 if you saw this live",
    "nobody is talking about this {streamer} moment 😱 comment YES if you want more",
    "this {streamer} clip got me dead 😂 comment your reaction 👇",
    "the chat when this happened 💀 {streamer} never misses. drop a ❤️",
    "HOW did {streamer} do this 🤯 comment if you could do better",
    "this {streamer} moment went crazy 🔥 tag someone who needs to see this",
    "not {streamer} really doing this live 😭 comment 1 if you watched the full stream",
    "{streamer} on another level rn 🎯 drop a 💯 if this is fire",
    "the reaction says everything 😂 {streamer} is built different. comment 🔥 or 💀",
]


def install_requirements():
    """Auto-install required packages"""
    packages = ["yt-dlp", "instagrapi", "moviepy"]
    for pkg in packages:
        print(f"Installing {pkg}...")
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], check=True)
    print("✅ All packages installed\n")


def load_posted():
    if Path(POSTED_FILE).exists():
        with open(POSTED_FILE) as f:
            return set(json.load(f))
    return set()


def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted), f)


def load_streams():
    if not Path(STREAMS_FILE).exists():
        with open(STREAMS_FILE, "w") as f:
            f.write("# Add YouTube stream links here, one per line\n")
            f.write("# Example:\n")
            f.write("# https://youtube.com/watch?v=XXXXXXXXXXX\n")
        print(f"📝 Created {STREAMS_FILE} — add your YouTube links there and restart.")
        sys.exit(0)
    with open(STREAMS_FILE) as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    return lines


def get_video_duration(url):
    """Get video duration in seconds using yt-dlp"""
    result = subprocess.run(
        ["yt-dlp", "--get-duration", "--no-warnings", url],
        capture_output=True, text=True
    )
    parts = result.stdout.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(parts[0])
    except:
        return 14400  # Default 4 hours if can't detect


def download_stream(url, output_path):
    """Download stream at lower quality for speed"""
    print(f"  ⬇️  Downloading stream (this may take a while)...")
    subprocess.run([
        "yt-dlp",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "--merge-output-format", "mp4",
        "-o", str(output_path),
        "--no-warnings",
        url
    ], check=True)
    print(f"  ✅ Downloaded: {output_path}")


def make_clip(input_path, start_sec, duration, output_path):
    """Cut and crop clip to vertical 9:16 using ffmpeg"""
    # Crop to vertical 9:16 from center of video
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", str(int(start_sec)),
        "-i", str(input_path),
        "-t", str(int(duration)),
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path),
        "-loglevel", "error"
    ], check=True)


def find_viral_moments(duration, count=20):
    """
    Find the best moments to clip.
    Spreads clips across the stream, biased toward middle/end
    where streams usually peak.
    """
    moments = []
    # Avoid first 10 min and last 5 min
    safe_start = 600
    safe_end = duration - 300
    usable = safe_end - safe_start

    # Bias toward middle and end (where good stuff happens)
    for i in range(count):
        bias = random.choices(
            ["early", "middle", "late"],
            weights=[0.15, 0.40, 0.45]
        )[0]
        if bias == "early":
            start = safe_start + random.uniform(0, usable * 0.33)
        elif bias == "middle":
            start = safe_start + random.uniform(usable * 0.25, usable * 0.65)
        else:
            start = safe_start + random.uniform(usable * 0.55, usable)

        # Vary clip length between 20-55 seconds (optimal for Reels)
        clip_duration = random.randint(20, 55)

        # Make sure clip doesn't go past end
        if start + clip_duration > safe_end:
            start = safe_end - clip_duration - 5

        moments.append((int(start), clip_duration))

    # Sort by timestamp, remove duplicates too close together
    moments.sort()
    filtered = [moments[0]]
    for m in moments[1:]:
        if m[0] - filtered[-1][0] > 60:  # At least 60s apart
            filtered.append(m)

    # Fill back up to count if we filtered too many
    while len(filtered) < count:
        start = random.randint(safe_start, int(safe_end - 55))
        filtered.append((start, random.randint(20, 55)))

    return filtered[:count]


def generate_caption():
    template = random.choice(CAPTION_TEMPLATES)
    caption = template.format(streamer=STREAMER_NAME)
    return f"{caption}\n.\n.\n.\n{HASHTAGS}"


def post_to_instagram(clip_path, caption):
    """Post a single video clip to Instagram Reels"""
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired

    cl = Client()
    session_file = Path("instagram_session.json")

    # Load saved session or login fresh
    if session_file.exists():
        try:
            cl.load_settings(session_file)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            print("  📱 Logged in via saved session")
        except LoginRequired:
            print("  🔑 Session expired, logging in fresh...")
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            cl.dump_settings(session_file)
    else:
        print("  🔑 Logging into Instagram (first time)...")
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(session_file)
        print("  ✅ Session saved for next time")

    # Post as Reel
    print(f"  📤 Uploading to Instagram Reels...")
    media = cl.clip_upload(
        Path(clip_path),
        caption=caption
    )
    print(f"  ✅ Posted! Media ID: {media.pk}")
    return str(media.pk)


def process_stream(url, stream_index, posted):
    """Download a stream and create 20 clips from it"""
    stream_id = f"stream_{stream_index}_{url[-11:]}"
    video_path = CLIPS_DIR / f"{stream_id}_full.mp4"

    # Check if already downloaded
    if not video_path.exists():
        download_stream(url, video_path)
    else:
        print(f"  ♻️  Using cached download: {video_path.name}")

    # Get duration
    duration = get_video_duration(url)
    print(f"  ⏱  Stream duration: {duration//3600}h {(duration%3600)//60}m")

    # Find viral moments
    moments = find_viral_moments(duration, count=20)
    clips = []

    print(f"  ✂️  Creating 20 clips...")
    for i, (start, dur) in enumerate(moments):
        clip_id = f"{stream_id}_clip{i:02d}_s{start}"

        if clip_id in posted:
            print(f"    ⏭  Clip {i+1} already posted, skipping")
            continue

        clip_path = CLIPS_DIR / f"{clip_id}.mp4"

        if not clip_path.exists():
            try:
                make_clip(video_path, start, dur, clip_path)
                print(f"    ✅ Clip {i+1:02d} — {start//60}:{start%60:02d} ({dur}s)")
            except Exception as e:
                print(f"    ❌ Clip {i+1} failed: {e}")
                continue

        clips.append((clip_id, clip_path))

    return clips


def main():
    print("=" * 50)
    print("  ClipEngine — Neon Clipping Auto-Poster")
    print("=" * 50)
    print()

    # Install packages on first run
    try:
        import instagrapi
        import moviepy
    except ImportError:
        print("📦 First run — installing required packages...\n")
        install_requirements()

    # Check ffmpeg
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode != 0:
        print("❌ ffmpeg not found!")
        print("   Install it: https://ffmpeg.org/download.html")
        print("   Or on Mac: brew install ffmpeg")
        print("   Or on Ubuntu: sudo apt install ffmpeg")
        sys.exit(1)

    if INSTAGRAM_PASSWORD == "YOUR_PASSWORD_HERE":
        print("❌ You haven't set your Instagram password yet!")
        print(f"   Open this file and change INSTAGRAM_PASSWORD on line 20")
        sys.exit(1)

    streams = load_streams()
    if not streams:
        print(f"❌ No streams found in {STREAMS_FILE}")
        print("   Add YouTube links (one per line) and restart.")
        sys.exit(1)

    print(f"📺 Found {len(streams)} stream(s) to process")
    print(f"📅 Will post {CLIPS_PER_DAY} clips/day ({len(streams) * CLIPS_PER_DAY} total)")
    print(f"⏱  {DELAY_BETWEEN_POSTS//60} minutes between each post")
    print()

    posted = load_posted()
    all_clips = []

    # Process all streams and build clip queue
    for i, url in enumerate(streams):
        print(f"\n🎬 Processing Stream {i+1}/{len(streams)}: {url}")
        try:
            clips = process_stream(url, i, posted)
            all_clips.extend(clips)
            print(f"  📦 {len(clips)} clips ready from stream {i+1}")
        except Exception as e:
            print(f"  ❌ Stream {i+1} failed: {e}")
            continue

    if not all_clips:
        print("\n❌ No clips to post. All may already be posted or processing failed.")
        sys.exit(0)

    print(f"\n🚀 Starting to post — {len(all_clips)} clips queued")
    print(f"   One at a time, {DELAY_BETWEEN_POSTS//60} min apart\n")

    posted_today = 0
    day_start = datetime.now()

    for clip_id, clip_path in all_clips:
        # Reset daily counter at midnight
        now = datetime.now()
        if now.date() > day_start.date():
            posted_today = 0
            day_start = now

        # Enforce daily limit
        if posted_today >= CLIPS_PER_DAY:
            # Wait until next day
            tomorrow = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0)
            wait_sec = (tomorrow - now).total_seconds()
            print(f"\n😴 Daily limit reached ({CLIPS_PER_DAY} posts). Waiting until tomorrow 8am...")
            time.sleep(wait_sec)
            posted_today = 0
            day_start = datetime.now()

        if clip_id in posted:
            continue

        print(f"\n📤 Posting clip {posted_today + 1}/{CLIPS_PER_DAY} — {clip_path.name}")
        caption = generate_caption()

        try:
            post_to_instagram(clip_path, caption)
            posted.add(clip_id)
            save_posted(posted)
            posted_today += 1

            print(f"  ✅ Posted successfully! ({posted_today}/{CLIPS_PER_DAY} today)")
            print(f"  💤 Waiting {DELAY_BETWEEN_POSTS//60} minutes before next post...")
            time.sleep(DELAY_BETWEEN_POSTS)

        except Exception as e:
            print(f"  ❌ Post failed: {e}")
            print(f"  ⏳ Waiting 5 minutes before retrying...")
            time.sleep(300)

    print("\n🎉 All clips posted! Add more streams to streams.txt and restart.")


if __name__ == "__main__":
    main()
