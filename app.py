import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# تكوين الصفحة
st.set_page_config(page_title="محلل الأسهم الفني", page_icon="📈")

# العنوان
st.title("محلل الأسهم الفني")
st.subheader("أداة للتحليل الفني للأسهم بالعربية")

# إدخال رمز السهم
رمز_السهم = st.text_input("رمز السهم (مثال: AAPL لشركة أبل)", value="AAPL")

# اختيار الفترة الزمنية
فترة = st.selectbox(
    "الفترة الزمنية",
    options=["1mo", "3mo", "6mo", "1y"],
    index=2
)

# زر التحليل
تحليل = st.button("تحليل")

# وظيفة جلب البيانات
def جلب_بيانات(رمز):
    try:
        data = yf.download(رمز, period="6mo")
        return data
    except:
        return None

# عند النقر على زر التحليل
if تحليل:
    # عرض رسالة تحميل
    with st.spinner("جاري تحميل البيانات..."):
        # جلب البيانات
        data = جلب_بيانات(رمز_السهم)
    
    # التحقق من وجود بيانات
    if data is not None and not data.empty:
        # عرض الرسم البياني
        st.write(f"الرسم البياني لسهم {رمز_السهم}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='سعر الإغلاق'))
        fig.update_layout(title=f"سعر سهم {رمز_السهم}", xaxis_title="التاريخ", yaxis_title="السعر")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # عرض آخر 5 أيام من البيانات
        st.write("آخر 5 أيام:")
        st.dataframe(data.tail())
    else:
        st.error(f"لا يمكن العثور على بيانات للرمز: {رمز_السهم}")
