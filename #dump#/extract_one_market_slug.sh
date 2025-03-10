curl -s "https://gamma-api.polymarket.com/markets?slug=russia-x-ukraine-ceasefire-in-2025" > market.json

question=$(grep -o '"question":"[^"]*"' market.json | head -n1 | sed 's/"question":"\(.*\)"/\1/')
outcomes=$(grep -o '"outcomes":"\[[^]]*\]' market.json | sed 's/.*\[\(.*\)\]/\1/' | tr -d '"' | tr ',' ';')
outcomePrices=$(grep -o '"outcomePrices":"\[[^]]*\]' market.json | sed 's/.*\[\(.*\)\]/\1/' | tr -d '"' | tr ',' ';')
liquidity=$(grep -o '"liquidity":[0-9.]*' market.json | head -n1 | cut -d':' -f2)
volume=$(grep -o '"volume":[0-9.]*' market.json | head -n1 | cut -d':' -f2)
endDate=$(grep -o '"endDate":"[^"]*"' market.json | head -n1 | sed 's/"endDate":"\(.*\)"/\1/')

output_file="market_data.csv"
if [ ! -f "$output_file" ]; then
  echo "question,outcomes,outcomePrices,liquidity,volume,endDate" > "$output_file"
fi

echo "\"$question\",\"$outcomes\",\"$outcomePrices\",$liquidity,$volume,$endDate" >> "$output_file"