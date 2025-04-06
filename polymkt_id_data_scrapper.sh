# Unfortunatly, Polymarket heavily uses Javascript. I was allowed to get the full source using a python script html_loader.py, this means that the crontab will need to go to the correct python environement, dashenv in our case.

source /home/ubuntu/dashenv/bin/activate

# Check argument
if [ -z "$1" ]; then
  echo "Usage: $0 <slug>"
  exit 1
fi

SLUG="$1"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "[INFO] Timestamp: $TIMESTAMP"
echo "[INFO] Slug: $SLUG"

# Paths NEED TO BE COMPLETE FOR CRON.
BASE_DIR="/home/ubuntu/Polymarket_Scrapper"
HTML_FILE="$BASE_DIR/db/html/polymarket_loaded_source.html"
CSV_FILE="$BASE_DIR/db/csv/market_${SLUG}_history.csv"

FLAT_CSV_FILE="$BASE_DIR/db/csv/snapshots/${SLUG}/flatdata_${TIMESTAMP}.csv"
mkdir -p "$(dirname "$FLAT_CSV_FILE")"

mkdir -p "$(dirname "$CSV_FILE")"

echo "[INFO] Running HTML loader with retry (max 5 attempts)..."

MAX_ATTEMPTS=5
ATTEMPT=1
SUCCESS=0

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "[INFO] Attempt $ATTEMPT of $MAX_ATTEMPTS..."
    python3 "$BASE_DIR/html_loader.py" "$SLUG"
    HTML_EXIT_CODE=$?

    if [ $HTML_EXIT_CODE -eq 0 ]; then
        echo "[INFO] html_loader.py success on attempt $ATTEMPT"
        SUCCESS=1
        break
    else
        echo "[WARNING] html_loader.py failed (exit code $HTML_EXIT_CODE)"
        ((ATTEMPT++))
        sleep 5  # wait before retrying
    fi
done

if [ $SUCCESS -ne 1 ]; then
    echo "[ERROR] html_loader.py failed after $MAX_ATTEMPTS attempts. Aborting..."
    exit 1
fi

# Extract the <script id="__NEXT_DATA__"> block content (JSON)
echo "[INFO] Extracting __NEXT_DATA__ block..."
JSON_RAW=$(grep -oP '<script id="__NEXT_DATA__" type="application/json"[^>]*>\K.*?(?=</script>)' "$HTML_FILE")

JSON_FILTERED="$JSON_RAW"

# DEBUG
# echo "[DEBUG] JSON_FILTERED:"
# echo "$JSON_FILTERED"

# Escape for CSV (double quotes doubled, semicolons replaced)
JSON_ESCAPED=$(echo "$JSON_FILTERED" | sed 's/"/""/g; s/;/,/g')

# Write header if first time (raw JSON log file)
if [ ! -f "$CSV_FILE" ]; then
  echo "timestamp;json_raw_content" > "$CSV_FILE"
fi

# (DEBUG) Raw JSON line
# echo "$TIMESTAMP;\"$JSON_ESCAPED\"" >> "$CSV_FILE"

###############################################
#       EXTRACTION OF COLUMNS AND DATA        #
###############################################
echo "[INFO] Extracting Columns and Data."

QUERIES_BLOCK=$(echo "$JSON_FILTERED" | grep -oP '"queries":\[\{"state":\{"data":\{.*?\}\}' | sed 's/^"queries":\[{"state":{"data":{//; s/}}$//')

MARKET_BLOCK=$(echo "$JSON_FILTERED" | grep -oP '"markets":\[\{.*?\}\]' | sed 's/^"markets":\[{//; s/}]$//')

# DEBUG (optionnel)
# echo "[DEBUG] QUERIES_BLOCK:"
# echo "$QUERIES_BLOCK"
# echo "[DEBUG] MARKET_BLOCK:"
# echo "$MARKET_BLOCK"

DATA_FIELDS=$(echo "$QUERIES_BLOCK" | grep -oP '"[^"]+"\s*:\s*("[^"]*"|[0-9.eE+-]+|true|false|null)' \
              | sed 's/^[[:space:]]*"//;s/"[[:space:]]*:[[:space:]]*/=/' | sed 's/^/data_/')

MARKET_FIELDS=$(echo "$MARKET_BLOCK" | grep -oP '"[^"]+"\s*:\s*("[^"]*"|[0-9.eE+-]+|true|false|null)' \
                | sed 's/^[[:space:]]*"//;s/"[[:space:]]*:[[:space:]]*/=/' | sed 's/^/market_/')

ALL_FIELDS=$( (echo "$DATA_FIELDS"; echo "$MARKET_FIELDS") )
ALL_KEYS=$(echo "$ALL_FIELDS" | sed 's/=.*//' | sort -u)

HEADER="timestamp"
for key in $ALL_KEYS; do
  HEADER="$HEADER;$key"
done
HEADER=$(echo "$HEADER" | sed 's/;$//')

FINAL_LINE="$TIMESTAMP"
for key in $ALL_KEYS; do
  val=$(echo "$ALL_FIELDS" | grep "^$key=" | head -n1 | sed 's/^[^=]*=//' | sed 's/;/,/g')
  FINAL_LINE="$FINAL_LINE;$val"
done
FINAL_LINE=$(echo "$FINAL_LINE" | sed 's/;$//')

if [ ! -f "$FLAT_CSV_FILE" ]; then
  echo "$HEADER" >> "$FLAT_CSV_FILE"
fi

echo "$FINAL_LINE" >> "$FLAT_CSV_FILE"
echo "[INFO] Done"
