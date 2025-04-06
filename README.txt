This project is a full-stack dashboard built to monitor prediction markets on [Polymarket](https://polymarket.com). It scrapes market data directly from the website (via a headless browser due to heavy JavaScript usage), logs the data as CSV snapshots, and displays key metrics in a live Dash interface.


- Data Scraper (`polymkt_id_data_scrapper.sh`)*:
  - Uses a headless Chromium browser (`playwright`) to extract the full HTML content.
  - Parses embedded JSON (`__NEXT_DATA__`) to extract market metrics.
  - Saves one CSV snapshot per execution, including a timestamp in the filename to avoid format mismatch issues across time.

- Data Aggregation (`ts_data_parser_slug.py`):
  - Loads all CSV snapshots for a given market.
  - Computes the intersection of columns across all files to ensure structural consistency.
  - Provides cleaned data to the dashboard.

- Dashboard (`webapp.py`):
  - Built with `Dash` and `Plotly`.
  - Displays interactive time-series of selected metrics.
  - Includes a 7-day moving average overlay, market health summary, option expected value computation, and an auto-generated daily report.
  - Refreshes every 5 minutes.

- Automation (`cron + tmux`):
  - The scraper runs every 5 minutes via `crontab`.
  - The web server runs continuously in a `tmux` session on an EC2 instance.


Setup Instructions

1. Download the files and requirements, do playwright install. 
2. Setup the cron job
3. Run the dashboard.
