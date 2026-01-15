import streamlit as st
import pandas as pd

# 1. إعداد الصفحة وتوجيه النص لليمين (RTL)
st.set_page_config(page_title="نظام استعلام المتدربين", layout="wide", page_icon="🎓")

# تخصيص التصميم باستخدام CSS لدعم اللغة العربية بشكل جميل
st.markdown("""
<style>
    .main {
        direction: rtl;
        text-align: right;
    }
    div.stButton > button:first-child {
        background-color: #0083B8;
        color: white;
        border-radius: 10px;
        width: 100%;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px;
        color: #0083B8;
    }
    h1, h2, h3 {
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .reportview-container .markdown-text-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* محاذاة الجداول */
    .stDataFrame {
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

# 2. تحميل البيانات
@st.cache_data
def load_data():
    try:
        # قراءة الملف - تأكد من أن الملف بنفس المسار
        df = pd.read_csv("data (1).csv")
        # تحويل الأرقام إلى نصوص لتجنب الفواصل العشرية في المعرفات
        df['رقم المتدرب'] = df['رقم المتدرب'].astype(str)
        df['رقم الجوال'] = df['رقم الجوال'].astype(str)
        return df
    except FileNotFoundError:
        return None

df = load_data()

# 3. القائمة الجانبية (شاشة البداية والخيارات)
st.sidebar.title("📌 لوحة التحكم")
page = st.sidebar.radio("الذهاب إلى:", ["الرئيسية والإحصائيات", "بحث عن متدرب"])

if df is not None:
    # --- الصفحة الرئيسية ---
    if page == "الرئيسية والإحصائيات":
        st.title("🎓 بوابة شؤون المتدربين")
        st.markdown("### مرحباً بك في نظام استعراض بيانات المتدربين")
        st.info("هذا النظام يتيح لك البحث عن بيانات المتدربين وجداولهم الدراسية بسهولة.")
        
        st.markdown("---")
        
        # عرض إحصائيات عامة (شاشة البداية)
        col1, col2, col3 = st.columns(3)
        
        total_students = df['رقم المتدرب'].nunique()
        total_courses = df['اسم المقرر'].nunique()
        departments = df['القسم'].unique()
        
        with col1:
            st.metric("عدد المتدربين", total_students)
        with col2:
            st.metric("المقررات المطروحة", total_courses)
        with col3:
            st.metric("عدد الأقسام", len(departments))
            
        st.markdown("---")
        st.subheader("📚 التخصصات المتاحة في النظام")
        
        # عرض التخصصات كبطاقات أو قائمة
        specializations = df['التخصص'].unique()
        for spec in specializations:
            count = df[df['التخصص'] == spec]['رقم المتدرب'].nunique()
            st.success(f"**{spec}** (عدد الطلاب: {count})")

    # --- صفحة البحث ---
    elif page == "بحث عن متدرب":
        st.title("🔍 البحث عن متدرب")
        
        search_query = st.text_input("أدخل اسم المتدرب أو الرقم التدريبي:", placeholder="مثال: 44321xxxxx أو سلطان...")
        
        if search_query:
            # البحث الجزئي بالاسم أو المطابق بالرقم
            mask = df['اسم المتدرب'].str.contains(search_query, na=False) | (df['رقم المتدرب'] == search_query)
            results = df[mask]
            
            # استخراج قائمة الأرقام التدريبية الفريدة من نتائج البحث
            found_ids = results['رقم المتدرب'].unique()
            
            if len(found_ids) == 0:
                st.warning("لم يتم العثور على متدرب بهذا الاسم أو الرقم.")
            else:
                st.write(f"تم العثور على **{len(found_ids)}** نتيجة:")
                
                # التكرار عبر كل طالب وجدناه (لعرض بياناته بشكل منفصل)
                for student_id in found_ids:
                    student_data = df[df['رقم المتدرب'] == student_id]
                    
                    # نأخذ البيانات الشخصية من الصف الأول (لأنها مكررة)
                    info = student_data.iloc[0]
                    
                    with st.container():
                        st.markdown(f"## 👤 {info['اسم المتدرب']}")
                        
                        # بطاقة المعلومات الشخصية
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("الرقم التدريبي", info['رقم المتدرب'])
                        c2.metric("التخصص", info['التخصص'])
                        c3.metric("المعدل التراكمي", info['المعدل التراكمي'])
                        c4.metric("الحالة", info['حالة المتدرب'])
                        
                        st.text(f"📱 رقم الجوال: {info['رقم الجوال']}")
                        st.text(f"🏢 القسم: {info['القسم']}")
                        
                        # جدول المواد
                        st.subheader("📋 الجدول الدراسي والمقررات")
                        courses_table = student_data[['رمز المقرر', 'اسم المقرر', 'الوحدات المعتمدة']]
                        st.table(courses_table)
                        
                        st.markdown("---")

else:
    st.error("ملف البيانات data (1).csv غير موجود. الرجاء وضعه في نفس مجلد البرنامج.")