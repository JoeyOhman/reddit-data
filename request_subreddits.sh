#!/bin/bash

YEAR=2021

declare -a Subreddits=("sweden" "Svenska" "svepol" "svenskpolitik" "PrivatEkonomi" "Aktiemarknaden" "Fotografi" "Snus" "spop" "swegan" "hogskoleprovet" "ankdammen" "ISKbets" "Allsvenskan" "SWARJE" "Swirclejerk" "sverigedemokraterna" "arbetarrorelsen" "skitswedditsager" "swedents" "pinsamt" "Asksweddit" "swedishproblems" "intresseklubben" "Spel" "Matlagning" "Pappaskamt" "SwedishCopypasta" "Boras" "gavle" "Gothenburg" "Halmstad" "helsingborg" "Jonkoping" "linkoping" "Lund" "Malmoe" "umea" "karlstad" "Vasteras" "skellefte" "stockholm" "uppsala" "orebro" "ostersund" "linkopinguniversity" "chalmers" "Falkenberg" "kth" "denmark" "norge")

for sub in "${Subreddits[@]}"; do
   echo "Downloading subreddit $sub for year $YEAR"
   python3 pushshift_api.py --subreddit $sub --year $YEAR
done
# python3 pushshift_api.py --subreddit svepol --year 2021 &