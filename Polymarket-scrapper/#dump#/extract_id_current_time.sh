# -------- PARAMÈTRE --------
market_id="$1"
if [ -z "$market_id" ]; then
  echo "Usage: $0 <market_id>"
  exit 1
fi

# -------- CHEMINS --------
tmp_file="./tmp/market_${market_id}.json"
output_file="./db/market_${market_id}_history.csv"

# -------- RÉCUPÉRATION JSON --------
curl -s "https://gamma-api.polymarket.com/markets/$market_id" > "$tmp_file"

# -------- HORODATAGE --------
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# -------- EXTRACTION CHAMPS --------
question=$(grep -o '"question":"[^"]*"' "$tmp_file" | sed 's/"question":"\(.*\)"/\1/')
slug=$(grep -o '"slug":"[^"]*"' "$tmp_file" | sed 's/"slug":"\(.*\)"/\1/')
endDate=$(grep -o '"endDate":"[^"]*"' "$tmp_file" | sed 's/"endDate":"\(.*\)"/\1/')
startDate=$(grep -o '"startDate":"[^"]*"' "$tmp_file" | sed 's/"startDate":"\(.*\)"/\1/')
liquidity=$(grep -o '"liquidity":[0-9.]*' "$tmp_file" | cut -d':' -f2)
volume=$(grep -o '"volume":[0-9.]*' "$tmp_file" | head -n 1 | cut -d':' -f2)
outcomes=$(grep -o '"outcomes":"\[[^]]*\]' "$tmp_file" | sed 's/.*\[\(.*\)\]/\1/' | tr -d '"' | tr ',' ';')
outcomePrices=$(grep -o '"outcomePrices":"\[[^]]*\]' "$tmp_file" | sed 's/.*\[\(.*\)\]/\1/' | tr -d '"' | tr ',' ';')
lastTradePrice=$(grep -o '"lastTradePrice":[0-9.]*' "$tmp_file" | cut -d':' -f2)
bestBid=$(grep -o '"bestBid":[0-9.]*' "$tmp_file" | cut -d':' -f2)
bestAsk=$(grep -o '"bestAsk":[0-9.]*' "$tmp_file" | cut -d':' -f2)
volume24hr=$(grep -o '"volume24hr":[0-9.]*' "$tmp_file" | cut -d':' -f2)
oneDayPriceChange=$(grep -o '"oneDayPriceChange":[0-9.]*' "$tmp_file" | cut -d':' -f2)

# -------- EN-TÊTE CSV (création si inexistant) --------
if [ ! -f "$output_file" ]; then
  echo "timestamp,question,slug,startDate,endDate,outcomes,outcomePrices,lastTradePrice,bestBid,bestAsk,liquidity,volume,volume24hr,oneDayPriceChange" > "$output_file"
fi

# -------- AJOUT DE LA LIGNE --------
echo "$timestamp,\"$question\",\"$slug\",$startDate,$endDate,\"$outcomes\",\"$outcomePrices\",$lastTradePrice,$bestBid,$bestAsk,$liquidity,$volume,$volume24hr,$oneDayPriceChange" >> "$output_file"