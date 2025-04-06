import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
# helper scripts are in the same directory
try:
    from ts_data_parser_slug import data_parser
    from daily_report import get_daily_report_table, export_daily_report 
except ImportError as e:
     print(f"Warning: Could not import helper modules: {e}")
     def data_parser(slug): return pd.DataFrame()
     def get_daily_report_table(df): return html.P("Daily report module missing.")
     def export_daily_report(df, path): pass

import datetime
import json 


# -------- Parameters --------
MARKET_SLUG = "us-recession-in-2025"
REFRESH_INTERVAL_SECONDS = 300 # Refresh every 5 minutes (adjust as needed)
DAILY_REPORT_PATH = f"db/market_{MARKET_SLUG}_daily_report.csv" 


# -------- Global variable to track daily update --------
LAST_DAILY_UPDATE_DATE = None


# -------- Load Time Series Data --------
def load_data():
    """Loads and preprocesses time series data from the main CSV file."""
    print(f"Loading data for {MARKET_SLUG}...") # Add print statement
    try:
        df = data_parser(MARKET_SLUG)
        if df is None or df.empty:
             print(f"Warning: data_parser returned empty DataFrame for {MARKET_SLUG}.")
             return pd.DataFrame()

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df.dropna(subset=['timestamp'], inplace=True)
            if not df.empty:
                 df = df.sort_values("timestamp")
                 print(f"Data loaded successfully: {len(df)} rows.") # Add success message
            else:
                 print("Warning: DataFrame empty after timestamp conversion.")
                 return pd.DataFrame()
        else:
            print("Error: 'timestamp' column not found after parsing.")
            return pd.DataFrame()
    except FileNotFoundError:
        print(f"Error: Data file for {MARKET_SLUG} not found. Using mock data?")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()
    return df

# -------- Export Daily Report --------
def update_and_export_daily_report(df):
    """Computes and exports the daily report."""
    if df is None or df.empty:
        print("Skipping daily report export: DataFrame is empty.")
        return
    if 'timestamp' not in df.columns or not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        print("Skipping daily report: Invalid 'timestamp' column.")
        return

    try:
        report_dir = os.path.dirname(DAILY_REPORT_PATH)
        if not os.path.exists(report_dir):
            print(f"Creating directory for daily report: {report_dir}")
            os.makedirs(report_dir, exist_ok=True)

        # Assuming export_daily_report function exists and works
        output_path = export_daily_report(df, DAILY_REPORT_PATH)
        if output_path:
             print(f"Daily report exported to {DAILY_REPORT_PATH}")
    except Exception as e:
        print(f"Error exporting daily report: {e}")


# -------- List of relevant numeric metrics for selection --------
RELEVANT_METRICS = ["data_lastTradePrice", "data_bestBid", "data_bestAsk", "data_volume", "data_volume24hr", "data_liquidity", "data_spread", "data_oneDayPriceChange"] # Simplified list based on mock data

# -------- Create Dash app --------
app = dash.Dash(__name__)
app.title = f"Polymarket Dashboard - {MARKET_SLUG}"

# -------- Layout Definition --------
app.layout = html.Div(style={"fontFamily": "Arial, sans-serif", "padding": "1rem 2rem", "backgroundColor": "#f4f6f6"}, children=[
    html.H1(id="market-title", children=f"Polymarket Dashboard - {MARKET_SLUG}", style={"textAlign": "center", "color": "#2c3e50", "marginBottom": "1.5rem"}),

    dcc.Interval(id="interval-component", interval=REFRESH_INTERVAL_SECONDS * 1000, n_intervals=0),

    html.Div(id="refresh-timer", style={"textAlign": "center", "fontSize": "0.9rem", "color": "#555", "marginBottom": "1.5rem"}),

    # --- Controls Row ---
    html.Div([
        html.Div([
            html.Label("Time Range:", style={"fontWeight": "bold", "marginRight": "0.5rem"}),
            dcc.Dropdown(
                id="time-range-selector", options=[{"label": "All", "value": "all"}, {"label": "7D", "value": "7d"}, {"label": "30D", "value": "30d"}, {"label": "90D", "value": "90d"}], value="all", clearable=False,
                style={"width": "120px", "display": "inline-block", "verticalAlign": "middle"}
            )
        ], style={"display": "inline-block", "marginRight": "2rem"}),

        html.Div([
            html.Label("Metrics:", style={"fontWeight": "bold", "marginRight": "0.5rem"}),
            dcc.Dropdown(
                id="metric-selector", options=[], value=[], multi=True, placeholder="Select metrics...",
                style={"width": "400px", "display": "inline-block", "verticalAlign": "middle"}
            )
        ], style={"display": "inline-block", "marginRight": "2rem"}), # Added margin

        # --- MOVING AVERAGE CHECKLIST ---
         html.Div([
            dcc.Checklist(
                id='ma-checklist',
                options=[{'label': 'Show 7-Day MA', 'value': 'MA7'}], value=[],
                labelStyle={'display': 'inline-block'},
                style={'display': 'inline-block', 'verticalAlign': 'middle'} # Align with dropdowns
            )
        ], style={'display': 'inline-block'}),
        # --- END MOVING AVERAGE CHECKLIST ---

    ], style={"textAlign": "center", "marginBottom": "2rem"}),


    # --- Main Content Area (Graph/Metrics + Option Pricer) ---
     html.Div([
        # Left Column: Metrics & Graphs
        html.Div(id="metrics-and-graphs", style={"width": "65%", "display": "inline-block", "verticalAlign": "top", "paddingRight": "1%"}),

        # Right Column: Option Pricer
        html.Div([
             # --- Option Pricer Section ---
            html.Div([
                html.H3("Option Expected Value", style={"textAlign": "center", "color": "#333", "marginTop": "0", "marginBottom": "1rem", "fontSize": "1.2em"}),
                html.Div([
                    html.Label("Strike (0-1):", style={"marginRight": "0.5rem"}),
                    dcc.Input(id="strike-price-input", type="number", placeholder="0.5", value=0.5, min=0, max=1, step=0.01, style={"width": "80px"}),
                ], style={"textAlign": "center", "marginBottom": "0.8rem"}),
                html.Div([
                    html.Div(id="call-option-price-output", style={"fontWeight": "bold", "fontSize": "1rem", "minHeight": "1.1em", "marginBottom":"0.3rem"}),
                    html.Div(id="put-option-price-output", style={"fontWeight": "bold", "fontSize": "1rem", "minHeight": "1.1em"}),
                ], style={"textAlign": "center", "padding": "0.8rem", "backgroundColor": "#e9ecef", "borderRadius": "5px"})
            ], style={"padding": "1rem", "border": "1px solid #ddd", "borderRadius": "8px", "backgroundColor": "#fff"}),
            # --- End Option Pricer Section ---

        ], style={"width": "33%", "display": "inline-block", "verticalAlign": "top", "paddingLeft": "1%"}),

    ], style={"width": "100%", "marginBottom": "2rem"}),


    # --- Bottom Row: Tables ---
    html.Div([
        html.Div(id="market-health-table", style={"display": "inline-block", "width": "48%", "verticalAlign": "top", "marginRight":"2%"}),
        html.Div(id="daily-report-table", style={"display": "inline-block", "width": "48%", "verticalAlign": "top"})
    ])
])


# -------- Main Callback --------
@app.callback(
    Output("market-title", "children"),
    Output("metric-selector", "options"),
    Output("metric-selector", "value"),
    Output("metrics-and-graphs", "children"),
    Output("market-health-table", "children"),
    Output("daily-report-table", "children"),
    Output("call-option-price-output", "children"),
    Output("put-option-price-output", "children"),
    Input("interval-component", "n_intervals"),
    Input("time-range-selector", "value"),
    Input("metric-selector", "value"),
    Input("strike-price-input", "value"),
    Input("ma-checklist", "value") # moving average
)
def update_layout_and_pricer(n, time_range, selected_metrics_input, strike_price, ma_checklist_value): 
    """Handles dashboard updates, loads data, calculates reports, option prices, and moving averages."""
    global LAST_DAILY_UPDATE_DATE

    print(f"\n--- Refresh cycle {n} ---")

    # --- Load Data ---
    df = load_data()

    # --- Initialize Output Defaults ---
    default_title = f"Polymarket Dashboard - {MARKET_SLUG}"
    metric_opts = []
    metric_vals = []
    # Use Div for placeholder to allow styling
    metrics_graphs_content = html.Div("Loading data...", style={'textAlign': 'center', 'padding': '2rem', 'border': '1px solid #ddd', 'backgroundColor':'#fff', 'borderRadius':'8px'})
    health_table_content = html.Div(html.H3("Market Health Info", style={"textAlign": "center", "color": "#333"}), style={"padding":"1rem", "border":"1px solid #ddd", "backgroundColor":"#fff", "borderRadius":"8px"})
    daily_table_content = html.Div(html.H3("Daily Report", style={"textAlign": "center", "color": "#333"}), style={"padding":"1rem", "border":"1px solid #ddd", "backgroundColor":"#fff", "borderRadius":"8px"})
    call_price_str = "N/A"
    put_price_str = "N/A"

    # --- Process Data if Available ---
    if not df.empty:
        # --- Dynamic Title ---
        market_title_text = df['data_question'].iloc[0] if 'data_question' in df.columns and not df['data_question'].empty else MARKET_SLUG
        default_title = f"Polymarket Market - {market_title_text}"

        # --- Dynamic Metric Options ---
        available_metrics = [col for col in RELEVANT_METRICS if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        metric_opts = [{"label": col.replace("data_", ""), "value": col} for col in available_metrics]
        default_selected_metrics = [col for col in ["data_lastTradePrice", "data_bestBid", "data_bestAsk"] if col in available_metrics]
        current_selected_metrics = [m for m in selected_metrics_input if m in available_metrics] if selected_metrics_input else default_selected_metrics
        metric_vals = current_selected_metrics

        # --- Daily Report Update Logic ---
        now = datetime.datetime.now(datetime.timezone.utc)
        current_date = now.date()
        scheduled_time = datetime.time(hour=20, minute=0) # 8 PM UTC
        if now.time() >= scheduled_time and (LAST_DAILY_UPDATE_DATE is None or LAST_DAILY_UPDATE_DATE != current_date):
            print("Attempting to update daily report...")
            update_and_export_daily_report(df.copy())
            LAST_DAILY_UPDATE_DATE = current_date
            print(f"Daily update date check complete. Last update attempt for date: {LAST_DAILY_UPDATE_DATE}")


        # --- Time Range Filtering ---
        df_filtered = df.copy()
        if time_range != "all":
            try:
                days = int(time_range.replace("d", ""))
                if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                     # Ensure comparison is timezone-naive or both are UTC
                    cutoff_date = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=days)
                    df_filtered = df[df["timestamp"].dt.tz_localize(None) >= cutoff_date].copy()
                else: print("Warning: Cannot apply time filter, timestamp column invalid.")
            except ValueError: print(f"Warning: Invalid time range value '{time_range}'. Using all data.")


        # --- Generate Components if Filtered Data Exists ---
        if not df_filtered.empty:
            latest = df_filtered.iloc[-1]

             # --- CALCULATE MOVING AVERAGE ---
            df_processed = df_filtered.copy() 
            show_ma = 'MA7' in ma_checklist_value # Check if checkbox is ticked

            if show_ma and 'timestamp' in df_processed.columns:
                try:
                    df_processed = df_processed.set_index('timestamp')
                    print("Calculating 7-Day Moving Averages...")
                    for metric in current_selected_metrics:
                        if metric in df_processed.columns and pd.api.types.is_numeric_dtype(df_processed[metric]):
                            ma_col_name = f"{metric}_MA7"
                            df_processed[ma_col_name] = df_processed[metric].rolling(window='7D', min_periods=1).mean()
                    df_processed = df_processed.reset_index()
                except Exception as e:
                    print(f"Error calculating moving average: {e}")
                    show_ma = False # Disable MA plotting if calculation fails
                    df_processed = df_filtered.copy() # Revert


            # --- Metrics Display ---
            metrics_display = []
            for metric in current_selected_metrics:
                 value = latest.get(metric)
                 value_str = f"{value:.4f}" if pd.notna(value) and isinstance(value, (int, float)) else str(value or 'N/A')
                 metrics_display.append(html.P(f"{metric.replace('data_', '')}: {value_str}"))

            metrics_block = html.Div([
                html.H3("Current Metrics", style={"marginBottom": "1rem", "color": "#2c3e50"}),
                html.P(f"Last Update: {latest.get('timestamp', pd.NaT).strftime('%Y-%m-%d %H:%M:%S UTC') if pd.notna(latest.get('timestamp')) else 'N/A'}", style={"marginBottom": "0.5rem"}),
            ] + metrics_display, style={
                "padding": "1rem", "backgroundColor": "#ffffff", "borderRadius": "8px", "boxShadow": "0px 1px 4px rgba(0, 0, 0, 0.1)", "marginBottom":"1rem"
            })

            # --- Time Series Graph ---
            graph_traces = []
            for metric in current_selected_metrics:
                # Plot raw metric if it exists and is numeric
                if metric in df_processed.columns and pd.api.types.is_numeric_dtype(df_processed[metric]):
                     graph_traces.append(go.Scatter(
                         x=df_processed["timestamp"], y=df_processed[metric], mode="lines", name=metric.replace("data_", "")
                     ))
                     # Plot Moving Average if requested and available
                     ma_col_name = f"{metric}_MA7"
                     if show_ma and ma_col_name in df_processed.columns:
                          graph_traces.append(go.Scatter(
                              x=df_processed["timestamp"], y=df_processed[ma_col_name], mode="lines", name=f"{metric.replace('data_', '')} 7D MA",
                              line=dict(dash='dash', width=1.5), opacity=0.8
                          ))

            time_series_graph = dcc.Graph(
                figure={ "data": graph_traces,
                         "layout": go.Layout(title="Time Series", xaxis={"title": "Timestamp"}, yaxis={"title": "Value"},
                                              margin={"l": 50, "r": 20, "t": 40, "b": 40}, hovermode="x unified",
                                              plot_bgcolor="#f9f9f9", paper_bgcolor="#ffffff", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
                       }
            ) if graph_traces else html.P("Select numeric metric(s) to display graph.")

            metrics_graphs_content = html.Div([metrics_block, time_series_graph], style={"border": "1px solid #ddd", "backgroundColor":"#fff", "borderRadius":"8px", "padding":"1rem"})


            # --- Market Health Table ---
            health_keys = ["data_question", "data_conditionId", "data_startDate", "data_endDate", "data_resolutionSource", "data_restricted", "data_archived", "data_acceptingOrders", "data_closed", "data_active"]
            health_info = [(key.replace("data_", ""), str(latest.get(key, "N/A"))) for key in health_keys]
            health_table_rows = [html.Tr([html.Th("Field", style={'border': '1px solid #ccc', 'padding': '6px', 'textAlign': 'left'}), html.Th("Value", style={'border': '1px solid #ccc', 'padding': '6px', 'textAlign': 'left'})])] + \
                                [html.Tr([html.Td(k, style={'border': '1px solid #ccc', 'padding': '6px'}), html.Td(v, style={'border': '1px solid #ccc', 'padding': '6px', 'wordBreak': 'break-word'})]) for k, v in health_info]
            health_table_content = html.Div([
                html.H3("Market Health Info", style={"textAlign": "center", "color": "#333", "fontSize":"1.2em"}),
                html.Table(health_table_rows, style={"width": "100%", "borderCollapse": "collapse", "fontSize":"0.9em"})
            ], style={"padding":"1rem", "border":"1px solid #ddd", "backgroundColor":"#fff", "borderRadius":"8px"})


            # --- Daily Report Table ---
            try:
                # Pass original df for full daily report history
                daily_table_content = get_daily_report_table(df) if 'get_daily_report_table' in globals() else html.P("Daily report function missing.")
                 # Wrap daily table for consistent styling
                daily_table_content = html.Div(daily_table_content, style={"padding":"1rem", "border":"1px solid #ddd", "backgroundColor":"#fff", "borderRadius":"8px"})
            except Exception as e:
                 print(f"Error generating daily report table: {e}")
                 daily_table_content = html.Div(html.P("Error generating daily report table.", style={'color': 'red'}), style={"padding":"1rem", "border":"1px solid #ddd", "backgroundColor":"#fff", "borderRadius":"8px"})


            # --- Option Pricing Logic ---
            call_price_str = "Enter Strike Price"
            put_price_str = ""
            if strike_price is not None:
                try:
                    K = float(strike_price)
                    price_col = 'data_lastTradePrice'
                    if 0 <= K <= 1 and price_col in latest and pd.notna(latest[price_col]):
                        P = float(latest[price_col])
                        call_value = P * max(0, 1 - K)
                        put_value = (1 - P) * max(0, K - 0)
                        call_price_str = f"Call Exp. Value: ${call_value:.4f}"
                        put_price_str = f"Put Exp. Value: ${put_value:.4f}"
                    elif not (0 <= K <= 1): call_price_str = "Strike must be 0 to 1"
                    else: call_price_str = "Price data unavailable"
                except (ValueError, TypeError): call_price_str = "Invalid Strike Input"


        else: # df_filtered is empty
            metrics_graphs_content = html.Div(f"No data available for the selected time range '{time_range}'.", style={'textAlign': 'center', 'padding': '2rem', 'border': '1px solid #ddd', 'backgroundColor':'#fff', 'borderRadius':'8px'})
            call_price_str = "N/A (No current data)"
            put_price_str = ""


    else: # Initial df load failed
         default_title = f"Polymarket Dashboard - {MARKET_SLUG} (Data Load Error)"
         metrics_graphs_content = html.Div("Error loading data. Check console/logs.", style={'color': 'red', 'textAlign': 'center', 'padding': '2rem', 'border': '1px solid #ddd', 'backgroundColor':'#fff', 'borderRadius':'8px'})
         call_price_str = "N/A (Load Error)"
         put_price_str = ""


    # --- Return all components in correct order ---
    return (
        default_title,
        metric_opts,
        metric_vals,
        metrics_graphs_content,
        health_table_content,
        daily_table_content,
        call_price_str,
        put_price_str
        # No return for Order Book in this version
    )


# -------- Refresh Timer Callback --------
@app.callback(
    Output("refresh-timer", "children"),
    Input("interval-component", "n_intervals")
)
def update_timer(n):
    """Updates the refresh timer display."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Scraper logic removed, so just show last check time
    return f"Last checked: {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}"

# -------- Run Server --------
if __name__ == '__main__':
    print("Starting Dash application...")
    try:
         FLAT_DATA_CSV_PATH = f"db/csv/market_{MARKET_SLUG}_flatdata.csv"
         os.makedirs(os.path.dirname(FLAT_DATA_CSV_PATH), exist_ok=True)
         print(f"Directory '{os.path.dirname(FLAT_DATA_CSV_PATH)}' checked/created.")
         os.makedirs(os.path.dirname(DAILY_REPORT_PATH), exist_ok=True)
         print(f"Directory '{os.path.dirname(DAILY_REPORT_PATH)}' checked/created.")
    except Exception as e:
         print(f"Error creating directories: {e}")
    app.run(host='0.0.0.0', port=8050, debug=True)