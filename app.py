import streamlit as st
import pandas as pd
import base64

# 1. إعداد الصفحة وتوجيه النص لليمين (RTL)
st.set_page_config(page_title="نظام شؤون المتدربين", layout="wide", page_icon="🎓")

# تخصيص التصميم CSS 
st.markdown("""
<style>
    .main { direction: rtl; text-align: right; background-color: #f9f9f9; }
    
    /* تنسيق العناوين */
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: right; }
    
    /* بطاقات المعلومات */
    div.stInfo, div.stWarning, div.stSuccess {
        text-align: right !important;
    }
    
    /* تنسيق الجدول */
    .stDataFrame { direction: rtl; }
    
    /* شاشة البداية */
    .hero-container {
        text-align: center;
        padding: 40px;
        background: linear-gradient(90deg, #0083B8 0%, #005c81 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 2. تحميل البيانات
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data (1).csv")
        # تنظيف البيانات (إزالة الفواصل العشرية من الأرقام)
        df['رقم المتدرب'] = df['رقم المتدرب'].astype(str).str.replace(r'\.0', '', regex=True)
        df['رقم الجوال'] = df['رقم الجوال'].astype(str).str.replace(r'\.0', '', regex=True)
        return df
    except FileNotFoundError:
        return None

df = load_data()

# 3. دالة توليد تقرير للطباعة (بدون حساب المتبقي)
def create_html_report(student_info, courses_df):
    total_units = courses_df['الوحدات المعتمدة'].sum()
    
    html = f"""
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; padding: 40px; text-align: right; }}
            h1 {{ color: #0083B8; text-align: center; border-bottom: 2px solid #0083B8; padding-bottom: 10px; }}
            .info-box {{ border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #fcfcfc; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; }}
            th {{ background-color: #0083B8; color: white; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <h1>تقرير المتدرب الأكاديمي</h1>
        
        <div class="info-box">
            <h3>👤 البيانات الشخصية</h3>
            <table style="border: none;">
                <tr>
                    <td style="border: none;"><strong>الاسم:</strong> {student_info['اسم المتدرب']}</td>
                    <td style="border: none;"><strong>الرقم التدريبي:</strong> {student_info['رقم المتدرب']}</td>
                </tr>
                <tr>
                    <td style="border: none;"><strong>التخصص:</strong> {student_info['التخصص']}</td>
                    <td style="border: none;"><strong>القسم:</strong> {student_info['القسم']}</td>
                </tr>
                <tr>
                    <td style="border: none;"><strong>المعدل التراكمي:</strong> {student_info['المعدل التراكمي']}</td>
                    <td style="border: none;"><strong>حالة المتدرب:</strong> {student_info['حالة المتدرب']}</td>
                </tr>
            </table>
        </div>
        
        <h3>📋 سجل المقررات المسجلة</h3>
        {courses_df.to_html(index=False)}
        
        <p style="margin-top: 15px; font-weight: bold;">إجمالي الوحدات المسجلة في هذا الكشف: {total_units}</p>
        
        <div class="footer">
            تم استخراج هذا التقرير آلياً من نظام شؤون المتدربين
        </div>
        
        <script>window.print();</script>
    </body>
    </html>
    """
    return html

# 4. الواجهة الرئيسية
if df is not None:
    # --- شاشة البداية ---
    st.markdown("""
    <div class="hero-container">
        <h1>🎓 بوابة خدمات المتدربين</h1>
        <h3>نظام الاستعلام عن الجداول والبيانات الأكاديمية</h3>
    </div>
    """, unsafe_allow_html=True)

    # --- منطقة البحث ---
    col_search, col_spacer = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔎 ابحث باسم المتدرب أو الرقم التدريبي:", placeholder="ادخل البيانات هنا...")

    if search_query:
        mask = df['اسم المتدرب'].str.contains(search_query, na=False) | (df['رقم المتدرب'] == search_query)
        results = df[mask]
        found_ids = results['رقم المتدرب'].unique()
        
        if len(found_ids) == 0:
            st.warning("⚠️ لا توجد نتائج مطابقة.")
        else:
            for student_id in found_ids:
                student_data = df[df['رقم المتدرب'] == student_id]
                info = student_data.iloc[0]
                
                with st.container():
                    st.markdown("---")
                    st.markdown(f"## 📄 ملف المتدرب: {info['اسم المتدرب']}")
                    
                    # عرض البيانات
                    c1, c2, c3, c4 = st.columns(4)
                    c1.info(f"**الرقم التدريبي:**\n{info['رقم المتدرب']}")
                    c2.info(f"**التخصص:**\n{info['التخصص']}")
                    c3.success(f"**القسم:**\n{info['القسم']}")
                    c4.warning(f"**المعدل:**\n{info['المعدل التراكمي']}")

                    # جدول المواد
                    st.subheader("المقررات المسجلة")
                    courses_table = student_data[['رمز المقرر', 'اسم المقرر', 'الوحدات المعتمدة']]
                    st.dataframe(courses_table, use_container_width=True, hide_index=True)
                    
                    # زر الطباعة (PDF)
                    report_html = create_html_report(info, courses_table)
                    b64 = base64.b64encode(report_html.encode('utf-8')).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="تقرير_{info["اسم المتدرب"]}.html" target="_blank" style="text-decoration:none;">'
                    
                    st.markdown(f"""
                    {href}
                    <button style="background-color: #c0392b; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; margin-top: 10px;">
                        🖨️ طباعة التقرير / حفظ كـ PDF
                    </button>
                    </a>
                    """, unsafe_allow_html=True)
                    
else:
    st.error("ملف البيانات data (1).csv غير موجود.")
