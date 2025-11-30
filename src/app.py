import streamlit as st
import ollama
import yfinance as yf
import plotly.graph_objects as go
import json
import pandas as pd
import time

# --- Page Config ---
st.set_page_config(
    page_title="EgySentiment Pro",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Modern Dark Theme) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Card Style */
    .metric-card {
        background: linear-gradient(145deg, #1E1E1E, #252525);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #444;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    .big-font {
        font-size: 56px !important;
        font-weight: 800;
        margin: 10px 0;
        background: -webkit-linear-gradient(45deg, #eee, #999);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sentiment Colors */
    .sent-positive { color: #00CC96 !important; -webkit-text-fill-color: #00CC96 !important; }
    .sent-negative { color: #EF553B !important; -webkit-text-fill-color: #EF553B !important; }
    .sent-neutral { color: #AB63FA !important; -webkit-text-fill-color: #AB63FA !important; }
    
    /* Input Area */
    .stTextArea textarea {
        background-color: #151920;
        border: 1px solid #333;
        border-radius: 12px;
        font-size: 16px;
        color: #eee;
    }
    .stTextArea textarea:focus {
        border-color: #00CC96;
        box-shadow: 0 0 0 1px #00CC96;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, #00CC96, #00A87E);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- Comprehensive Stock Mapping (EGX 30) ---
# Format: "Display Name": {"ticker": "TICKER.CA", "keywords": ["list", "of", "keywords"]}
STOCK_DATA = {
    # --- Banking Sector ---
    "Commercial International Bank (CIB)": {
        "ticker": "COMI.CA",
        "keywords": ["CIB", "COMI", "Commercial International Bank", "البنك التجاري الدولي", "التجاري الدولي", "CIB Egypt"]
    },
    "QNB Alahli": {
        "ticker": "QNBA.CA",
        "keywords": ["QNB", "QNBA", "Qatar National Bank", "بنك قطر الوطني", "قطر الوطني", "QNB Alahli", "بنك قطر الوطني الأهلي"]
    },
    "Crédit Agricole Egypt": {
        "ticker": "CIEB.CA",
        "keywords": ["Credit Agricole", "CIEB", "Crédit Agricole", "كريدي أجريكول", "بنك كريدي أجريكول"]
    },
    "Housing & Development Bank": {
        "ticker": "HDBK.CA",
        "keywords": ["HDBK", "Housing & Development Bank", "Housing and Development Bank", "بنك التعمير والإسكان", "التعمير والإسكان"]
    },
    "Faisal Islamic Bank of Egypt": {
        "ticker": "FAIT.CA",
        "keywords": ["Faisal Islamic Bank", "FAIT", "FAITA", "بنك فيصل الإسلامي", "فيصل الإسلامي"]
    },
    "Abu Dhabi Islamic Bank (ADIB)": {
        "ticker": "ADIB.CA",
        "keywords": ["ADIB", "Abu Dhabi Islamic Bank", "مصرف أبوظبي الإسلامي", "أبوظبي الإسلامي", "ADIB Egypt"]
    },
    "Al Baraka Bank Egypt": {
        "ticker": "SAUD.CA",
        "keywords": ["Al Baraka", "SAUD", "Al Baraka Bank", "بنك البركة", "البركة مصر"]
    },
    "Egyptian Gulf Bank (EGBANK)": {
        "ticker": "EGBE.CA",
        "keywords": ["EGBANK", "EGBE", "Egyptian Gulf Bank", "البنك المصري الخليجي", "المصري الخليجي"]
    },
    "Export Development Bank of Egypt (EBank)": {
        "ticker": "EXPA.CA",
        "keywords": ["EBank", "EXPA", "Export Development Bank", "البنك المصري لتنمية الصادرات", "تنمية الصادرات"]
    },

    # --- Non-Bank Financial Services ---
    "EFG Hermes": {
        "ticker": "HRHO.CA",
        "keywords": ["EFG Hermes", "HRHO", "EFG", "EFG Holding", "المجموعة المالية هيرميس", "هيرميس", "هيرميس القابضة"]
    },
    "E-Finance": {
        "ticker": "EFIH.CA",
        "keywords": ["E-Finance", "EFIH", "e-finance", "إي فاينانس", "اي فاينانس", "e-finance for Digital and Financial Investments"]
    },
    "Fawry": {
        "ticker": "FWRY.CA",
        "keywords": ["Fawry", "FWRY", "Fawry for Banking Technology", "فوري", "شركة فوري", "فوري للمدفوعات"]
    },
    "Belton Financial": {
        "ticker": "BTFH.CA",
        "keywords": ["Belton", "BTFH", "Belton Financial", "بلتون", "بلتون المالية", "بلتون القابضة"]
    },
    "CI Capital": {
        "ticker": "CICH.CA",
        "keywords": ["CI Capital", "CICH", "سي آي كابيتال", "سي اي كابيتال"]
    },

    # --- Real Estate & Construction ---
    "Talaat Moustafa Group (TMG)": {
        "ticker": "TMGH.CA",
        "keywords": ["Talaat Moustafa", "TMGH", "TMG", "TMG Holding", "طلعت مصطفى", "مجموعة طلعت مصطفى", "Madinaty", "Rehab City", "مدينتي", "الرحاب"]
    },
    "Palm Hills Developments": {
        "ticker": "PHDC.CA",
        "keywords": ["Palm Hills", "PHDC", "Palm Hills Developments", "بالم هيلز", "بالم هيلز للتعمير", "Badya", "بادية"]
    },
    "Sixth of October Development & Investment (SODIC)": {
        "ticker": "OCDI.CA",
        "keywords": ["SODIC", "OCDI", "Sixth of October Development", "سوديك", "السادس من أكتوبر للتنمية"]
    },
    "Madinet Masr (MNHD)": {
        "ticker": "MASR.CA",
        "keywords": ["Madinet Masr", "MASR", "Madinet Nasr", "MNHD", "مدينة مصر", "مدينة نصر للإسكان", "Taj City", "تاج سيتي"]
    },
    "Heliopolis Housing": {
        "ticker": "HELI.CA",
        "keywords": ["Heliopolis", "HELI", "Heliopolis Company for Housing", "مصر الجديدة", "مصر الجديدة للإسكان", "مصر الجديدة للاسكان والتعمير"]
    },
    "Orascom Construction": {
        "ticker": "ORAS.CA",
        "keywords": ["Orascom Construction", "ORAS", "Orascom", "أوراسكوم للإنشاءات", "أوراسكوم كونستراكشون"]
    },
    "Emaar Misr": {
        "ticker": "EMFD.CA",
        "keywords": ["Emaar", "EMFD", "Emaar Misr", "إعمار", "إعمار مصر", "Marassi", "مراسي"]
    },

    # --- Industrial & Basic Resources ---
    "Elsewedy Electric": {
        "ticker": "SWDY.CA",
        "keywords": ["Elsewedy", "SWDY", "El Sewedy", "Elsewedy Electric", "السويدي", "السويدي إليكتريك", "السويدي للكابلات"]
    },
    "Ezz Steel": {
        "ticker": "ESRS.CA",
        "keywords": ["Ezz Steel", "ESRS", "Ezz", "Al Ezz Dekheila", "حديد عز", "عز الدخيلة", "مجموعة عز"]
    },
    "Abu Qir Fertilizers": {
        "ticker": "ABUK.CA",
        "keywords": ["Abu Qir", "ABUK", "Abu Qir Fertilizers", "أبو قير", "أبو قير للأسمدة", "ابوقير"]
    },
    "Misr Fertilizers Production (MOPCO)": {
        "ticker": "MFPC.CA",
        "keywords": ["MOPCO", "MFPC", "Misr Fertilizers", "موبكو", "مصر لإنتاج الأسمدة"]
    },
    "Sidi Kerir Petrochemicals (SIDPEC)": {
        "ticker": "SKPC.CA",
        "keywords": ["Sidi Kerir", "SKPC", "Sidpec", "سيدي كرير", "سيدبك", "سيدي كرير للبتروكيماويات"]
    },
    "Alexandria Mineral Oils (AMOC)": {
        "ticker": "AMOC.CA",
        "keywords": ["AMOC", "Alexandria Mineral Oils", "أموك", "زيوت معدنية", "الاسكندرية للزيوت المعدنية"]
    },
    "Kima": {
        "ticker": "KIMA.CA",
        "keywords": ["Kima", "KIMA", "Egyptian Chemical Industries", "كيما", "الصناعات الكيماوية المصرية"]
    },

    # --- Telecom & Technology ---
    "Telecom Egypt (WE)": {
        "ticker": "ETEL.CA",
        "keywords": ["Telecom Egypt", "ETEL", "WE", "TE", "المصرية للاتصالات", "وي", "تي إي داتا"]
    },

    # --- Consumer & Healthcare ---
    "Eastern Company": {
        "ticker": "EAST.CA",
        "keywords": ["Eastern Company", "EAST", "Eastern Tobacco", "الشرقية للدخان", "ايسترن كومباني", "سجائر"]
    },
    "Juhayna Food Industries": {
        "ticker": "JUFO.CA",
        "keywords": ["Juhayna", "JUFO", "جهينة", "جهينه", "جهينة للصناعات الغذائية"]
    },
    "Edita Food Industries": {
        "ticker": "EFID.CA",
        "keywords": ["Edita", "EFID", "إيديتا", "ايديتا", "إيديتا للصناعات الغذائية"]
    },
    "Ibnsina Pharma": {
        "ticker": "ISPH.CA",
        "keywords": ["Ibnsina", "ISPH", "Ibnsina Pharma", "ابن سينا", "ابن سينا فارما"]
    },
    "Cleopatra Hospitals": {
        "ticker": "CLHO.CA",
        "keywords": ["Cleopatra", "CLHO", "Cleopatra Hospitals Group", "CHG", "مستشفيات كليوباترا", "مجموعة كليوباترا"]
    },
    "GB Corp (Ghabbour)": {
        "ticker": "GBCO.CA",
        "keywords": ["GB Corp", "GBCO", "GB Auto", "Ghabbour", "جي بي أوتو", "غبور", "جي بي كورب"]
    },

    # --- Others ---
    "Egypt Kuwait Holding": {
        "ticker": "EKHO.CA",
        "keywords": ["Egypt Kuwait Holding", "EKHO", "EKH", "القابضة المصرية الكويتية", "المصرية الكويتية"]
    },
    "Qalaa Holdings": {
        "ticker": "CCAP.CA",
        "keywords": ["Qalaa", "CCAP", "Citadel Capital", "القلعة", "القلعة للاستشارات المالية"]
    },
    "Egyptian Satellites (NileSat)": {
        "ticker": "EGSA.CA",
        "keywords": ["NileSat", "EGSA", "Egyptian Satellites", "نايل سات", "المصرية للأقمار الصناعية"]
    }
}

# --- Helper Functions ---
def analyze_text(text):
    try:
        response = ollama.chat(model='egysentiment', messages=[
            {'role': 'user', 'content': text},
        ])
        content = response['message']['content'].strip()
        
        # Robust JSON extraction
        start_idx = content.find("{")
        if start_idx != -1:
            end_idx = content.rfind("}")
            if end_idx != -1:
                content = content[start_idx:end_idx+1]
            else:
                # If closing brace is missing, try to append it
                content = content[start_idx:] + "}"
        
        result = json.loads(content)
        return result.get("sentiment", "neutral").lower(), result.get("reasoning", "")
    except Exception as e:
        return "neutral", f"Error: {str(e)} | Raw: {content if 'content' in locals() else 'No content'}"

def get_sentiment_score(sentiment):
    if sentiment == "positive": return 1
    if sentiment == "negative": return -1
    return 0

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/pyramids.png", width=64)
    st.title("EgySentiment")
    st.caption("v1.3 | Local Inference Engine")
    
    st.markdown("---")
    st.subheader("📈 Market Context")
    selected_name = st.selectbox(
        "Select Company",
        options=list(STOCK_DATA.keys()),
        index=0
    )
    selected_ticker = STOCK_DATA[selected_name]["ticker"]
    st.caption(f"Ticker: **{selected_ticker}**")
    
    st.markdown("---")
    st.info("💡 **Tip:** Use the 'Batch Processing' tab to generate features for your forecasting model.")

# --- Main Content ---
st.markdown("## 🦅 Financial Intelligence Dashboard")

tab1, tab2 = st.tabs(["⚡ Live Analysis", "🏭 Batch Processing (Forecasting)"])

# === TAB 1: LIVE ANALYSIS ===
with tab1:
    col1, col2 = st.columns([1.8, 1.2], gap="large")

    with col1:
        st.markdown("### 📰 News Analysis")
        news_text = st.text_area(
            "Input News Article", 
            height=180, 
            placeholder="Paste financial news here (e.g., 'CIB reports 30% profit growth in Q3...')...",
            label_visibility="collapsed"
        )
        
        analyze_btn = st.button("⚡ Analyze Sentiment", type="primary", use_container_width=True)

        if analyze_btn and news_text:
            with st.spinner("Processing article..."):
                sentiment, reasoning = analyze_text(news_text)
                
                # Display Results
                st.markdown("### Analysis Result")
                
                # Dynamic Color Class
                color_class = f"sent-{sentiment}"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin:0; color: #888; text-transform: uppercase; letter-spacing: 1px;">Detected Sentiment</h4>
                    <h1 class="big-font {color_class}">{sentiment.upper()}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                # Reasoning Box
                st.markdown(f"""
                <div style="background-color: #1E1E1E; border-left: 4px solid #444; padding: 16px; border-radius: 0 8px 8px 0;">
                    <strong style="color: #eee;">💡 Reasoning:</strong><br>
                    <span style="color: #ccc;">{reasoning}</span>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"### 📊 {selected_name}")
        
        # Fetch Data
        try:
            stock = yf.Ticker(selected_ticker)
            hist = stock.history(period="3mo")
            
            if not hist.empty:
                # Calculate Metrics
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = current_price - prev_price
                pct_change = (change / prev_price) * 100
                
                # Color for price change
                delta_color = "normal" 
                
                st.metric(
                    label="Last Close (EGP)", 
                    value=f"{current_price:.2f}", 
                    delta=f"{change:.2f} ({pct_change:.2f}%)",
                    delta_color=delta_color
                )
                
                # Interactive Chart
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    increasing_line_color='#00CC96', 
                    decreasing_line_color='#EF553B'
                )])
                
                fig.update_layout(
                    height=350,
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis_rangeslider_visible=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#888"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#333')
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Volume Bar
                st.caption("Volume (3mo)")
                st.bar_chart(hist['Volume'], height=100, color="#333333")
                
            else:
                st.warning(f"No market data available for {selected_ticker}")
                
        except Exception as e:
            st.error(f"Market Data Error: {e}")

# === TAB 2: BATCH PROCESSING ===
with tab2:
    st.markdown("### 🏭 Feature Extraction for Forecasting")
    st.markdown("Upload your historical news data and select a target stock. The app will automatically filter for relevant articles (using English/Arabic keywords) and generate sentiment scores.")
    
    uploaded_file = st.file_uploader("Upload CSV or JSONL", type=["csv", "jsonl"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_json(uploaded_file, lines=True)
            
            st.dataframe(df.head(), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                text_col = st.selectbox("Select Text Column", df.columns)
            with col2:
                date_col = st.selectbox("Select Date Column (Optional)", ["None"] + list(df.columns))
            with col3:
                # Smart Filter Dropdown
                target_stock = st.selectbox("Select Target Stock", ["None (Process All)"] + list(STOCK_DATA.keys()))
            
            # Filter Logic
            if target_stock != "None (Process All)":
                keywords = STOCK_DATA[target_stock]["keywords"]
                st.info(f"🔍 Filtering for **{target_stock}** using keywords: {', '.join(keywords)}")
                
                keyword_list = [k.strip().lower() for k in keywords]
                initial_count = len(df)
                # Filter rows where text contains ANY of the keywords
                df = df[df[text_col].astype(str).str.lower().apply(lambda x: any(k in x for k in keyword_list))]
                final_count = len(df)
                
                if final_count == 0:
                    st.warning("⚠️ No articles matched the selected stock. Try 'None' to process all.")
                else:
                    st.success(f"✅ Found **{final_count}** relevant articles (out of {initial_count}).")
            
            # Aggregation Option
            aggregate_daily = False
            if date_col != "None":
                aggregate_daily = st.checkbox("📅 Aggregate Scores by Day? (Recommended for Forecasting)", value=True)

            if st.button("🚀 Start Batch Processing", disabled=df.empty):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                sentiments = []
                scores = []
                
                total = len(df)
                start_time = time.time()
                
                # Iterate over the filtered dataframe
                for i, (index, row) in enumerate(df.iterrows()):
                    text = row[text_col]
                    
                    # Update UI
                    status_text.text(f"Processing {i+1}/{total}: {str(text)[:50]}...")
                    progress_bar.progress((i + 1) / total)
                    
                    # Inference
                    sent, _ = analyze_text(str(text))
                    score = get_sentiment_score(sent)
                    
                    sentiments.append(sent)
                    scores.append(score)
                
                # Add results
                df['sentiment'] = sentiments
                df['sentiment_score'] = scores
                
                # Handle Aggregation
                if aggregate_daily and date_col != "None":
                    try:
                        # Convert to datetime
                        df[date_col] = pd.to_datetime(df[date_col])
                        # Group by Date
                        daily_df = df.groupby(df[date_col].dt.date).agg({
                            'sentiment_score': 'mean',
                            text_col: 'count'  # Count articles per day
                        }).reset_index()
                        daily_df.rename(columns={text_col: 'article_count', 'sentiment_score': 'daily_sentiment_score'}, inplace=True)
                        
                        st.success(f"✅ Aggregated into {len(daily_df)} daily records!")
                        st.dataframe(daily_df.head(), use_container_width=True)
                        
                        # Download Aggregated
                        filename = f"{target_stock.replace(' ', '_')}_DAILY_features.csv" if target_stock != "None (Process All)" else "daily_sentiment_features.csv"
                        csv = daily_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"💾 Download Daily Features CSV",
                            data=csv,
                            file_name=filename,
                            mime='text/csv',
                        )
                    except Exception as e:
                        st.error(f"Aggregation Failed: {e}")
                        # Fallback to raw download
                        st.warning("Downloading raw data instead.")
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="💾 Download Raw Features CSV",
                            data=csv,
                            file_name='raw_features.csv',
                            mime='text/csv',
                        )
                else:
                    end_time = time.time()
                    duration = end_time - start_time
                    st.success(f"✅ Processed {total} items in {duration:.2f} seconds!")
                    
                    # Preview
                    st.dataframe(df[[text_col, 'sentiment', 'sentiment_score']].head(), use_container_width=True)
                    
                    # Download Raw
                    filename = f"{target_stock.replace(' ', '_')}_features.csv" if target_stock != "None (Process All)" else "egysentiment_features.csv"
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"💾 Download {filename}",
                        data=csv,
                        file_name=filename,
                        mime='text/csv',
                    )
                
        except Exception as e:
            st.error(f"Error processing file: {e}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>EgySentiment © 2024 | Financial Intelligence Unit</div>", unsafe_allow_html=True)
