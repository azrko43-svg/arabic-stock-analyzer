import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# تكوين الصفحة
st.set_page_config(page_title="محلل الأسهم الفني", page_icon="📈", layout="wide")

# العنوان
st.title("📈 محلل الأسهم الفني")
st.subheader("أداة للتحليل الفني للأسهم بالعربية")

# إدخال رمز السهم
col1, col2 = st.columns(2)

with col1:
    رمز_السهم = st.text_input("رمز السهم (مثال: AAPL لشركة أبل)", value="AAPL")

with col2:
    فترة = st.selectbox(
        "الفترة الزمنية",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=2,
        format_func=lambda x: {
            "1mo": "شهر واحد",
            "3mo": "3 أشهر",
            "6mo": "6 أشهر",
            "1y": "سنة واحدة",
            "2y": "سنتان"
        }[x]
    )

# زر التحليل
تحليل = st.button("🔍 تحليل", use_container_width=True)

# وظيفة حساب المتوسطات المتحركة
def حساب_مؤشرات(data):
    """حساب المؤشرات الفنية"""
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    # حساب RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    return data

# وظيفة جلب البيانات
def جلب_بيانات(رمز, فترة_زمنية):
    """جلب بيانات السهم من yfinance"""
    try:
        سهم = yf.Ticker(رمز)
        data = سهم.history(period=فترة_زمنية)
        
        if data.empty:
            return None, None
        
        # جلب معلومات الشركة
        معلومات = سهم.info
        
        return data, معلومات
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return None, None

# عند النقر على زر التحليل
if تحليل:
    with st.spinner("🔄 جاري تحميل البيانات..."):
        data, معلومات = جلب_بيانات(رمز_السهم, فترة)
    
    if data is not None and not data.empty:
        # حساب المؤشرات الفنية
        data = حساب_مؤشرات(data)
        
        # عرض معلومات الشركة
        if معلومات:
            st.success(f"✅ تم تحميل بيانات {معلومات.get('longName', رمز_السهم)}")
            
            # عرض المقاييس الأساسية
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "السعر الحالي",
                    f"${data['Close'].iloc[-1]:.2f}",
                    f"{((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100):.2f}%"
                )
            
            with col2:
                st.metric(
                    "أعلى سعر (52 أسبوع)",
                    f"${معلومات.get('fiftyTwoWeekHigh', 'N/A')}"
                )
            
            with col3:
                st.metric(
                    "أقل سعر (52 أسبوع)",
                    f"${معلومات.get('fiftyTwoWeekLow', 'N/A')}"
                )
            
            with col4:
                st.metric(
                    "حجم التداول",
                    f"{معلومات.get('volume', 'N/A'):,}" if معلومات.get('volume') else "N/A"
                )
        
        # الرسم البياني الرئيسي
        st.subheader("📊 الرسم البياني")
        
        # إنشاء رسم بياني بمؤشرات متعددة
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=('السعر والمتوسطات المتحركة', 'مؤشر القوة النسبية (RSI)')
        )
        
        # الشموع اليابانية
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='السعر'
            ),
            row=1, col=1
        )
        
        # المتوسط المتحرك 20
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA20'],
                mode='lines',
                name='MA20',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        # المتوسط المتحرك 50
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA50'],
                mode='lines',
                name='MA50',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        # مؤشر RSI
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # خطوط مرجعية لـ RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, opacity=0.5)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1, opacity=0.5)
        
        fig.update_layout(
            title=f"التحليل الفني لسهم {رمز_السهم}",
            xaxis_title="التاريخ",
            yaxis_title="السعر ($)",
            height=700,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        fig.update_yaxes(title_text="السعر ($)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # تحليل بسيط
        st.subheader("💡 ملخص التحليل")
        
        rsi_أخير = data['RSI'].iloc[-1]
        سعر_أخير = data['Close'].iloc[-1]
        ma20_أخير = data['MA20'].iloc[-1]
        ma50_أخير = data['MA50'].iloc[-1]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**إشارات المتوسطات المتحركة:**")
            if pd.notna(ma20_أخير) and pd.notna(ma50_أخير):
                if سعر_أخير > ma20_أخير and سعر_أخير > ma50_أخير:
                    st.success("🟢 السعر فوق المتوسطين - اتجاه صاعد")
                elif سعر_أخير < ma20_أخير and سعر_أخير < ma50_أخير:
                    st.error("🔴 السعر تحت المتوسطين - اتجاه هابط")
                else:
                    st.warning("🟡 السعر بين المتوسطين - اتجاه محايد")
        
        with col2:
            st.write("**مؤشر القوة النسبية (RSI):**")
            if pd.notna(rsi_أخير):
                if rsi_أخير > 70:
                    st.error(f"🔴 RSI = {rsi_أخير:.1f} - منطقة تشبع شرائي")
                elif rsi_أخير < 30:
                    st.success(f"🟢 RSI = {rsi_أخير:.1f} - منطقة تشبع بيعي")
                else:
                    st.info(f"🔵 RSI = {rsi_أخير:.1f} - منطقة محايدة")
        
        # عرض آخر 10 أيام من البيانات
        st.subheader("📋 آخر 10 أيام")
        بيانات_عرض = data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10).copy()
        بيانات_عرض.columns = ['الافتتاح', 'الأعلى', 'الأدنى', 'الإغلاق', 'الحجم']
        st.dataframe(بيانات_عرض.style.format({
            'الافتتاح': '${:.2f}',
            'الأعلى': '${:.2f}',
            'الأدنى': '${:.2f}',
            'الإغلاق': '${:.2f}',
            'الحجم': '{:,.0f}'
        }), use_container_width=True)
        
    else:
        st.error(f"❌ لا يمكن العثور على بيانات للرمز: {رمز_السهم}")
        st.info("تأكد من إدخال رمز السهم بشكل صحيح (مثال: AAPL, TSLA, GOOGL)")

# ملاحظة في الأسفل
st.markdown("---")
st.caption("⚠️ تنبيه: هذه الأداة للأغراض التعليمية فقط ولا تمثل نصيحة استثمارية.")
