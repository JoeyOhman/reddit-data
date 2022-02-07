#!/bin/bash

# YEAR=2017

# declare -a Subreddits=("sweden" "Svenska" "svepol" "svenskpolitik" "PrivatEkonomi" "Aktiemarknaden" "Fotografi" "Snus" "spop" "swegan" "hogskoleprovet" "ankdammen" "ISKbets" "Allsvenskan" "SWARJE" "Swirclejerk" "sverigedemokraterna" "arbetarrorelsen" "skitswedditsager" "swedents" "pinsamt" "Asksweddit" "swedishproblems" "intresseklubben" "Spel" "Matlagning" "Pappaskamt" "SwedishCopypasta" "Boras" "gavle" "Gothenburg" "Halmstad" "helsingborg" "Jonkoping" "linkoping" "Lund" "Malmoe" "umea" "karlstad" "Vasteras" "skellefte" "stockholm" "uppsala" "orebro" "ostersund" "linkopinguniversity" "chalmers" "Falkenberg" "kth" "denmark" "norge")

# for sub in "${Subreddits[@]}"; do
   # echo "Downloading subreddit $sub for year $YEAR"
   # python3 pushshift_api.py --subreddit $sub --year $YEAR
# done


# YEAR=2017
SUBREDDIT="Halmstad"

# declare -a years=(2021 2020 2019 2018 2017 2016 2015 2014 2013 2012 2011 2010 2009 2008 2007 2006)

# for year in "${years[@]}"; do
for year in {2006..2017}; do
   echo "Downloading subreddit $SUBREDDIT for year $year"
   python3 pushshift_api.py --subreddit $SUBREDDIT --year $year
   sleep 3
done
