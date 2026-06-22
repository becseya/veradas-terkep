#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$0")
OUTPUT_JS="../public/locations.js"

cd "$SCRIPT_DIR"

curl -X POST https://www.ovsz.hu/sites/all/scripts/gps2020/esemenyek-table.php \
     -d "latitude_percent=0.5" \
     -d "longitude_percent=0.5" \
     -d "kereses_radius=1000" \
     -d "idopontfoglalas=off" > events.html

cat events.html | python3 aggregate.py > locations.json
cat locations.json | python3 decorate.py > locations_decorated.json

# final output
echo "const LOCATIONS = " > "$OUTPUT_JS"
cat locations_decorated.json >> "$OUTPUT_JS"
echo ";" >> "$OUTPUT_JS"
echo "const DATE_SCRAPED_AT='$(date)';" >> "$OUTPUT_JS"

# print info
num_elements=$(cat locations_decorated.json | grep 'is_fixed_location' | wc -l)
echo "Processed $num_elements locations"
