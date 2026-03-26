import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Personal Expense Dashboard", layout="wide")

# Dashboard Title
st.title("📊 My Activity & Expense Dashboard")
st.markdown("---")

# 2. User ဆီကနေ Google Sheet Link တောင်းခံခြင်း
st.info("💡 သင့်ရဲ့ Google Sheet Link ကို အောက်တွင် ထည့်သွင်းပါ။ (Google Sheet ၏ Share permission ကို 'Anyone with the link > Viewer' ပေးထားရန် လိုအပ်ပါသည်)")

url = st.text_input("🔗 Google Sheet Link ထည့်ရန်", placeholder="https://docs.google.com/spreadsheets/d/...")

# URL ထည့်သွင်းပြီးမှသာ Dashboard ကို ဆက်လက် အလုပ်လုပ်စေမည်
if url:
    try:
        # 3. Google Sheet နှင့် ချိတ်ဆက်ခြင်း
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url)

        # Data Cleaning
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.sort_values(by='Date', ascending=False)

        if df.empty:
            st.warning("⚠️ Sheet ထဲတွင် အချက်အလက် (Data) မရှိသေးပါ။ Date column မှန်ကန်မှုရှိမရှိ စစ်ဆေးပါ။")
        else:
            # 4. Sidebar Filters
            st.sidebar.header("🔍 Filters")

            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            
            start_date = st.sidebar.date_input("စတင်မည့်ရက်", min_date)
            end_date = st.sidebar.date_input("ကုန်ဆုံးမည့်ရက်", max_date)

            categories = df['Type of Usage'].dropna().unique().tolist()
            selected_categories = st.sidebar.multiselect(
                "ကြည့်ချင်သည့် ကဏ္ဍများ ရွေးပါ", 
                options=categories, 
                default=categories
            )

            # Filter Apply လုပ်ခြင်း
            mask = (df['Date'].dt.date >= start_date) & \
                   (df['Date'].dt.date <= end_date) & \
                   (df['Type of Usage'].isin(selected_categories))
            
            filtered_df = df.loc[mask]

            # 5. Top Metric Cards
            total_amount = filtered_df['Amount'].sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric(label="💰 စုစုပေါင်း သုံးစွဲမှု", value=f"{total_amount:,.0f} MMK")
            
            if not filtered_df.empty:
                top_cat = filtered_df.groupby('Type of Usage')['Amount'].sum().idxmax()
                top_val = filtered_df.groupby('Type of Usage')['Amount'].sum().max()
                m2.metric(label="🔝 အသုံးအများဆုံး", value=str(top_cat), delta=f"{top_val:,.0f} MMK")
            else:
                m2.metric(label="🔝 အသုံးအများဆုံး", value="Data မရှိပါ")

            m3.metric(label="📅 စာရင်းအရေအတွက်", value=len(filtered_df))

            st.markdown("---")

            # 6. Charts Layout
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("အသုံးစရိတ် ရာခိုင်နှုန်း (%)")
                if not filtered_df.empty:
                    fig_pie = px.pie(
                        filtered_df, 
                        values='Amount', 
                        names='Type of Usage', 
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Chart ပြသရန် Data မရှိပါ။")

            with col2:
                st.subheader("အသုံးအများဆုံး ကဏ္ဍများ (Bar Chart)")
                if not filtered_df.empty:
                    cat_summary = filtered_df.groupby('Type of Usage')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
                    
                    fig_bar = px.bar(
                        cat_summary, 
                        x='Type of Usage', 
                        y='Amount', 
                        color='Type of Usage', 
                        text_auto=',.0f'  # <--- ဒီနေရာလေးကို ပြောင်းလိုက်တာပါ
                    )
                    
                    # Mouse ထောက်ရင် (Hover လုပ်ရင်) ပေါ်မယ့်စာသားကို သပ်သပ်ရပ်ရပ်ဖြစ်အောင် ပြင်မယ်
                    fig_bar.update_traces(
                        textposition='outside', # ဂဏန်းတွေကို Bar ရဲ့ အပေါ်မှာ ပြဖို့
                        hovertemplate="ကဏ္ဍ: %{x}<br>ပမာဏ: %{y:,.0f} 원<extra></extra>"
                    )
                    
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Chart ပြသရန် Data မရှိပါ။")

            # 7. Detailed Data Table
            st.subheader("📋 အသေးစိတ် စာရင်း")
            st.dataframe(filtered_df, use_container_width=True)

            # Update Button
            if st.button('🔄 Data အသစ်များကို ပြန်ဖတ်ရန်'):
                st.cache_data.clear()
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error တက်နေပါသည်: {e}")
        st.info("Google Sheet Link မှန်မမှန်နှင့် Column Header များ (Date, Amount, Type of Usage) မှန်ကန်စွာ ရှိမရှိ စစ်ဆေးပေးပါ။")
else:
    st.warning("⚠️ Dashboard ကြည့်ရှုရန် အထက်တွင် Google Sheet Link ကို အရင်ဆုံး ထည့်သွင်းပေးပါ။")