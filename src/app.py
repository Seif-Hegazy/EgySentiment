import streamlit as st
import ollama
import yfinance as yf
import plotly.graph_objects as go
import json
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="EgySentiment Dashboard",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Market Context ---
st.sidebar.title("📈 Market Context")
selected_ticker = st.sidebar.selectbox(
    "Select Ticker",
    ["COMI.CA", "EFIH.CA", "HRHO.CA", "EAST.CA", "SWDY.CA", "ETEL.CA", "TMGH.CA", "EKHO.CA", "ABUK.CA", "AMOC.CA"]
)

# --- Main Content ---
st.title("🇪🇬 EgySentiment Analyzer")
st.markdown("### AI-Powered Egyptian Financial News Sentiment")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📰 News Analysis")
    news_text = st.text_area("Paste financial news article here:", height=150, placeholder="E.g., CIB reports record-breaking profits for Q3 2024...")
    
    analyze_btn = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

    if analyze_btn and news_text:
        with st.spinner("🤖 Analyzing with Llama 3.1..."):
            try:
                # Call Ollama
                response = ollama.chat(model='egysentiment', messages=[
                    {'role': 'user', 'content': news_text},
                ])
                
                # Parse Response
                content = response['message']['content']
                # Attempt to fix potential JSON formatting issues (e.g. missing braces)
                if not content.strip().endswith("}"):
                    content += "}"
                if not content.strip().startswith("{"):
                    content = "{" + content.split("{", 1)[1]
                
                result = json.loads(content)
                sentiment = result.get("sentiment", "neutral").lower()
                reasoning = result.get("reasoning", "No reasoning provided.")
                
                # Display Results
                st.markdown("---")
                
                # Sentiment Metric
                color_map = {
                    "positive": "green",
                    "negative": "red",
                    "neutral": "gray"
                }
                color = color_map.get(sentiment, "blue")
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin:0; color: #888;">Sentiment</h3>
                    <h1 style="margin:0; font-size: 48px; color: {color}; text-transform: uppercase;">{sentiment}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                # Reasoning
                st.info(f"**💡 Reasoning:**\n\n{reasoning}")
                
            except Exception as e:
                st.error(f"Error analyzing text: {e}")
                st.code(response['message']['content']) # Show raw output for debugging

with col2:
    st.subheader(f"📊 {selected_ticker} Performance")
    
    # Fetch Data
    try:
        stock = yf.Ticker(selected_ticker)
        hist = stock.history(period="3mo")
        
        if not hist.empty:
            # Calculate Change
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            pct_change = (change / prev_price) * 100
            
            st.metric(label="Last Close", value=f"{current_price:.2f} EGP", delta=f"{change:.2f} ({pct_change:.2f}%)")
            
            # Plot Candle Chart
            fig = go.Figure(data=[go.Candlestick(x=hist.index,
                            open=hist['Open'],
                            high=hist['High'],
                            low=hist['Low'],
                            close=hist['Close'])])
            
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_rangeslider_visible=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found for this ticker.")
            
    except Exception as e:
        st.error(f"Could not load market data: {e}")

st.markdown("---")
st.caption("Powered by Llama 3.1-8B (Fine-Tuned) | Local Inference on Apple Silicon")
