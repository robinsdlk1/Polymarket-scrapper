# Accept market ID as first argument
if [ -z "$1" ]; then
  echo "Usage: $0 <market_id>"
  exit 1
fi
MARKET_ID="$1"

# Define output and temporary file paths based on the market ID
OUTPUT_FILE="./db/market_${MARKET_ID}_history.csv"
TMP_FILE="./tmp/market_${MARKET_ID}.json"

# Ensure the output directories exist
mkdir -p "$(dirname "$OUTPUT_FILE")" "$(dirname "$TMP_FILE")"

# Fetch JSON data from Polymarket's Gamma API for the given market ID
API_URL="https://gamma-api.polymarket.com/markets/${MARKET_ID}"
if ! curl -s -f "$API_URL" -o "$TMP_FILE"; then
  echo "Warning: Failed to fetch data for market $MARKET_ID (API call failed)" >&2
  exit 1
fi

# Verify that the response is not empty
if [ ! -s "$TMP_FILE" ]; then
  echo "Warning: No data received for market $MARKET_ID" >&2
  exit 1
fi

# Capture the current timestamp in UTC (ISO 8601 format)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Read the raw JSON response
JSON_DATA=$(cat "$TMP_FILE")

JSON_ESCAPED=$(echo "$JSON_DATA" | sed 's/"/""/g')

# Append timestamp and JSON to the CSV file (as a new line)
echo "$TIMESTAMP;\"$JSON_ESCAPED\"" >> "$OUTPUT_FILE"