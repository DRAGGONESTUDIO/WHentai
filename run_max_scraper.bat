@echo off
echo WHentai Maximum Videos Scraper
echo ==============================
echo This script will run all available scrapers to add as many videos as possible.
echo.

echo Current video count:
python -c "import json; data = json.load(open('videos.json', encoding='utf-8')); print(len(data))" 2>nul || echo 0

echo.
echo Running maximum videos scraper...
python max_videos_scraper.py

echo.
echo Final video count:
python -c "import json; data = json.load(open('videos.json', encoding='utf-8')); print(len(data))" 2>nul || echo 0

echo.
echo Scraping complete!
echo Check max_scraping_summary.json for detailed results.
echo.

pause