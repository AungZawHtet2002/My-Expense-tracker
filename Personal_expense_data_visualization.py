import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# [၁] Web Page ရဲ့ Tab နေရာမှာ ပေါ်မယ့် နာမည်နဲ့ မျက်နှာပြင် အကျယ်ကို သတ်မှတ်ခြင်း
st.set_page_config(page_title="Multi-Language Expense Tracker", layout="wide")

# ==========================================
# [၂] 🌐 Language Dictionary (ဘာသာစကား စာသားများ သိမ်းဆည်းခြင်း)
# Dictionary (Key-Value) ပုံစံနဲ့ မြန်မာ၊ English၊ Korean ၃ မျိုးအတွက် စာသားတွေကို သိမ်းထားတာပါ။
# နောက်ပိုင်း User ရွေးလိုက်တဲ့ ဘာသာစကားပေါ် မူတည်ပြီး ဒီထဲက စာသားတွေကို ဆွဲထုတ်သုံးပါမယ်။
# ==========================================
translations = {
    "မြန်မာ": {
        "title": "📊 အသုံးစရိတ်နှင့် လှုပ်ရှားမှု မှတ်တမ်း",
        "info": "💡 သင့်ရဲ့ Google Sheet Link ကို အောက်တွင် ထည့်သွင်းပါ။ (Share permission ကို 'Viewer' ပေးထားရန် လိုအပ်ပါသည်)",
        "link_prompt": "🔗 Google Sheet Link ထည့်ရန်",
        "filters": "🔍 စစ်ထုတ်ရန်",
        "start_date": "စတင်မည့်ရက်",
        "end_date": "ကုန်ဆုံးမည့်ရက်",
        "categories": "ကြည့်ချင်သည့် ကဏ္ဍများ ရွေးပါ",
        "total": "💰 စုစုပေါင်း သုံးစွဲမှု",
        "top": "🔝 အသုံးအများဆုံး",
        "count": "📅 စာရင်းအရေအတွက်",
        "pie_title": "အသုံးစရိတ် ရာခိုင်နှုန်း (%)",
        "bar_title": "အသုံးအများဆုံး ကဏ္ဍများ",
        "table_title": "📋 အသေးစိတ် စာရင်း",
        "update_btn": "🔄 Data ပြန်ဖတ်ရန်",
        "no_data": "⚠️ အချက်အလက် မရှိသေးပါ။",
        "error": "❌ Error တက်နေပါသည်: Link နှင့် Data ကို စစ်ဆေးပါ။",
        "warning": "⚠️ Dashboard ကြည့်ရှုရန် အထက်တွင် Google Sheet Link ကို ထည့်သွင်းပေးပါ။"
    },
    "English": {
        "title": "📊 Activity & Expense Dashboard",
        "info": "💡 Enter your Google Sheet Link below. (Ensure share permission is set to 'Viewer')",
        "link_prompt": "🔗 Enter Google Sheet Link",
        "filters": "🔍 Filters",
        "start_date": "Start Date",
        "end_date": "End Date",
        "categories": "Select Categories",
        "total": "💰 Total Expense",
        "top": "🔝 Top Category",
        "count": "📅 Total Records",
        "pie_title": "Expense by Category (%)",
        "bar_title": "Top Expenses by Category",
        "table_title": "📋 Detailed Records",
        "update_btn": "🔄 Sync Data",
        "no_data": "⚠️ No data available.",
        "error": "❌ Error: Please check your link and data.",
        "warning": "⚠️ Please enter a Google Sheet Link above to view the dashboard."
    },
    "한국어": {
        "title": "📊 내 지출 및 활동 대시보드",
        "info": "💡 아래에 구글 시트 링크를 입력하세요. (공유 권한을 '뷰어'로 설정해야 합니다)",
        "link_prompt": "🔗 구글 시트 링크 입력",
        "filters": "🔍 필터",
        "start_date": "시작일",
        "end_date": "종료일",
        "categories": "카테고리 선택",
        "total": "💰 총 지출",
        "top": "🔝 최대 지출처",
        "count": "📅 기록 수",
        "pie_title": "카테고리별 지출 비율 (%)",
        "bar_title": "가장 많이 쓴 카테고리",
        "table_title": "📋 상세 내역",
        "update_btn": "🔄 데이터 동기화",
        "no_data": "⚠️ 데이터가 없습니다.",
        "error": "❌ 오류: 링크와 데이터를 확인해주세요.",
        "warning": "⚠️ 대시보드를 보려면 위에 구글 시트 링크를 입력해주세요."
    }
}

# ==========================================
# [၃] ⚙️ Settings (User ထံမှ ဘာသာစကားနှင့် ငွေကြေးယူနစ် ရွေးချယ်ခိုင်းခြင်း)
# ==========================================
# မျက်နှာပြင်ကို ၂ ပိုင်း (၂ ကော်လံ) ခွဲလိုက်ပါတယ်
col_lang, col_curr = st.columns(2)

with col_lang:
    # Selectbox သုံးပြီး ဘာသာစကား ရွေးခိုင်းမယ်
    selected_lang = st.selectbox("🌐 Language / ဘာသာစကား / 언어", ["မြန်မာ", "English", "한국어"])

with col_curr:
    # Selectbox သုံးပြီး ငွေကြေးယူနစ် ရွေးခိုင်းမယ်
    selected_curr = st.selectbox("💵 Currency / ငွေကြေး ယူနစ်", ["MMK (Kyat)", "KRW (원)", "USD ($)", "EUR (€)", "THB (฿)"])

# ရွေးချယ်လိုက်တဲ့ ဘာသာစကားအရ အပေါ်က Dictionary ထဲက စာသားအုပ်စုကို ဆွဲထုတ်လိုက်တယ် (t ထဲကို ထည့်ထားတယ်)
t = translations[selected_lang]

# ဥပမာ- 'KRW (원)' လို့ ရွေးရင် Space ခြားထားတဲ့အရှေ့က 'KRW' ဆိုတဲ့ စာသားလေးကိုပဲ ဖြတ်ယူလိုက်တယ်
curr_symbol = selected_curr.split(" ")[0] 

# ခေါင်းစဉ်ကို ရွေးထားတဲ့ ဘာသာစကားနဲ့ ပြမယ်
st.title(t["title"])
st.markdown("---")

# ==========================================
# [၄] 🔗 Google Sheet Link တောင်းခံခြင်းနှင့် Data ဖတ်ခြင်း
# ==========================================
# ညွှန်ကြားချက် စာသားပြမယ်
st.info(t["info"])

# User ဆီက Link ရိုက်ထည့်ဖို့ Input box ခေါ်မယ်
url = st.text_input(t["link_prompt"], placeholder="https://docs.google.com/spreadsheets/d/...")

# User က url ထည့်လိုက်ပြီဆိုရင် အောက်ကလုပ်ငန်းစဉ်တွေ စလုပ်မယ်
if url:
    try:
        # Google Sheet နဲ့ ချိတ်ပြီး Data ကို ဖတ်မယ် (df ဆိုတဲ့ DataFrame ထဲ ထည့်မယ်)
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url)

        # [Data Cleaning] Date Column က စာသားတွေကို တကယ့် ရက်စွဲ Format ပြောင်းမယ်။ 
        # မှားနေတဲ့စာတွေပါရင် ဖြတ်ထုတ်မယ် (errors='coerce' နှင့် dropna သုံးထားသည်)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        # နောက်ဆုံးရက်စွဲတွေ အပေါ်ရောက်အောင် အစဉ်လိုက် စီမယ်
        df = df.sort_values(by='Date', ascending=False)

        # Data ဘာမှမရှိရင် သတိပေးစာပြမယ်
        if df.empty:
            st.warning(t["no_data"])
        else:
            # ==========================================
            # [၅] 🔍 Sidebar Filters (ဘေးဘောင်က စစ်ထုတ်သည့်အပိုင်း)
            # ==========================================
            st.sidebar.header(t["filters"])
            
            # Data ထဲက အစောဆုံးရက် နဲ့ နောက်ဆုံးရက်ကို ရှာမယ်
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            
            # User ကို Sidebar ကနေ Date ၂ ခု ရွေးခိုင်းမယ်
            start_date = st.sidebar.date_input(t["start_date"], min_date)
            end_date = st.sidebar.date_input(t["end_date"], max_date)

            # Data ထဲမှာ ပါတဲ့ Category တွေကို ထပ်မနေအောင် (unique) စုထုတ်ပြီး List လုပ်မယ်
            categories = df['Type of Usage'].dropna().unique().tolist()
            # User ကို Category တွေ အများကြီး (Multi-select) ရွေးခိုင်းမယ်
            selected_categories = st.sidebar.multiselect(
                t["categories"], 
                options=categories, 
                default=categories
            )

            # [Filter Data] ရွေးထားတဲ့ ရက်စွဲကြားထဲက၊ ရွေးထားတဲ့ Category တွေနဲ့ ကိုက်ညီတဲ့ Data တွေကိုပဲ စစ်ထုတ်မယ် (mask ထဲထည့်)
            mask = (df['Date'].dt.date >= start_date) & \
                   (df['Date'].dt.date <= end_date) & \
                   (df['Type of Usage'].isin(selected_categories))
            # စစ်ထုတ်ပြီးသား Data ကို filtered_df အနေနဲ့ သတ်မှတ်မယ်
            filtered_df = df.loc[mask]

            # ==========================================
            # [၆] 🔢 Metric Cards (အပေါ်ဆုံးက စုစုပေါင်း ဂဏန်းပြသည့် ကတ်များ)
            # ==========================================
            # Filter လုပ်ထားတဲ့ထဲက Amount တွေကို အကုန်ပေါင်းမယ်
            total_amount = filtered_df['Amount'].sum()
            
            # မျက်နှာပြင်ကို ၃ ပိုင်းခွဲမယ်
            m1, m2, m3 = st.columns(3)
            # ကတ် (၁) မှာ စုစုပေါင်းပြမယ် (ဂဏန်းတွေကို ကော်မာ ခြားပြဖို့ {total_amount:,.0f} သုံးထားတယ်)
            m1.metric(label=t["total"], value=f"{total_amount:,.0f} {curr_symbol}")
            
            # Category အလိုက် Amount ပေါင်းပြီး အများဆုံး Category နာမည်နဲ့ ပမာဏကို ရှာမယ်
            if not filtered_df.empty:
                top_cat = filtered_df.groupby('Type of Usage')['Amount'].sum().idxmax()
                top_val = filtered_df.groupby('Type of Usage')['Amount'].sum().max()
                # ကတ် (၂) မှာ အသုံးအများဆုံး နာမည်နဲ့ ပမာဏပြမယ်
                m2.metric(label=t["top"], value=str(top_cat), delta=f"{top_val:,.0f} {curr_symbol}")
            else:
                m2.metric(label=t["top"], value="-")

            # ကတ် (၃) မှာ စုစုပေါင်း Row (စာရင်း) ဘယ်နှခုရှိလဲ ပြမယ်
            m3.metric(label=t["count"], value=len(filtered_df))
            st.markdown("---")

            # ==========================================
            # [၇] 📊 Charts Layout (ဂရပ်ဖ်များ ဆွဲခြင်း)
            # ==========================================
            col1, col2 = st.columns(2)
            
            # (က) Pie Chart ဆွဲခြင်း
            with col1:
                st.subheader(t["pie_title"])
                if not filtered_df.empty:
                    # Plotly Express သုံးပြီး ဝိုင်းဝိုင်းလေး ဆွဲမယ်
                    fig_pie = px.pie(filtered_df, values='Amount', names='Type of Usage', hole=0.4)
                    # Mouse ထောက်ရင် (Hover) ပေါ်မယ့် စာသားကို မိမိရွေးထားတဲ့ ငွေကြေးနဲ့ ပြအောင် Custom လုပ်မယ်
                    fig_pie.update_traces(hovertemplate=f"Category: %{{label}}<br>Amount: %{{value:,.0f}} {curr_symbol}<extra></extra>")
                    st.plotly_chart(fig_pie, use_container_width=True)

            # (ခ) Bar Chart ဆွဲခြင်း
            with col2:
                st.subheader(t["bar_title"])
                if not filtered_df.empty:
                    # Category တူရာပေါင်းပြီး အများကနေ အနည်းကို စီမယ် (sort_values)
                    cat_summary = filtered_df.groupby('Type of Usage')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
                    # Plotly Express သုံးပြီး Bar Chart ဆွဲမယ် (text_auto=',.0f' ဖြင့် ဂဏန်းအတိအကျပြမယ်)
                    fig_bar = px.bar(cat_summary, x='Type of Usage', y='Amount', color='Type of Usage', text_auto=',.0f')
                    # Bar ရဲ့ အပေါ်မှာ စာသားပြဖို့နဲ့၊ Hover လုပ်ရင် ငွေကြေးယူနစ်နဲ့ ပေါ်အောင် ပြင်မယ်
                    fig_bar.update_traces(textposition='outside', hovertemplate=f"Category: %{{x}}<br>Amount: %{{y:,.0f}} {curr_symbol}<extra></extra>")
                    st.plotly_chart(fig_bar, use_container_width=True)

            # ==========================================
            # [၈] 📋 Table & Refresh Button
            # ==========================================
            st.subheader(t["table_title"])
            # Data အကြမ်းကို Table အနေနဲ့ အောက်ဆုံးမှာ ပြပေးမယ်
            st.dataframe(filtered_df, use_container_width=True)

            # User က Data အသစ်ထည့်ပြီးချိန်မှာ အလွယ်တကူ Refresh လုပ်နိုင်အောင် Button လေး ထည့်ထားတယ်
            if st.button(t["update_btn"]):
                st.cache_data.clear() # သိမ်းထားတဲ့ Cache ကို ဖျက်ပြီး Data အသစ်ပြန်ဖတ်ခိုင်းတာပါ
                st.rerun()

    except Exception as e:
        # Error တက်ခဲ့ရင် (ဥပမာ Link မှားတာ) အနီရောင်နဲ့ ပြမယ်
        st.error(t["error"])
else:
    # URL မထည့်ရသေးခင်မှာ သတိပေးစာလေးပဲ ပြထားမယ်
    st.warning(t["warning"])
