# app.py
# -*- coding: utf-8 -*-
"""
لوحة تحليلات الموارد البشرية لعلماء البيانات
تشغيل:
    pip install streamlit pandas numpy plotly scikit-learn
    streamlit run app.py

مهم:
- يجب وضع hr_master_clean.csv في نفس مجلد هذا الملف.
- الملف الحالي مبني بصيغة CSV بلا أسماء أعمدة صحيحة؛ لذلك نقرأه header=None
  ونعيد تسمية الحقول وفق بنية البيانات الفعلية المكتشفة.
- لا توجد أي أداة رفع ملفات؛ مصدر البيانات محلي وثابت.
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ============================================================
# 1) إعداد الصفحة
# ============================================================
st.set_page_config(
    page_title="HR Intelligence | علماء البيانات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2) الهوية البصرية + RTL
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #07111f;
        --panel: #0d1b2d;
        --panel2: #10243c;
        --blue: #3b82f6;
        --cyan: #22d3ee;
        --green: #10b981;
        --orange: #f97316;
        --red: #ef4444;
        --text: #f8fafc;
        --muted: #94a3b8;
        --border: rgba(148,163,184,.16);
    }

    html, body, [class*="css"] {
        font-family: "Cairo", sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 5%, rgba(37,99,235,.18), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(16,185,129,.10), transparent 24%),
            linear-gradient(135deg, #050b14 0%, #07111f 48%, #091a2e 100%);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081321 0%, #0b1930 100%);
        border-left: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        direction: rtl;
        text-align: right;
    }

    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    h1, h2, h3, h4, p, label, div {
        direction: rtl;
    }

    .hero {
        padding: 28px 30px;
        border: 1px solid rgba(59,130,246,.25);
        border-radius: 24px;
        background:
            linear-gradient(120deg, rgba(15,36,60,.96), rgba(7,18,33,.94)),
            radial-gradient(circle at 15% 30%, rgba(34,211,238,.12), transparent 30%);
        box-shadow: 0 18px 55px rgba(0,0,0,.28);
        margin-bottom: 20px;
        text-align: right;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.15rem;
        font-weight: 800;
        color: #ffffff;
    }

    .hero p {
        margin: 8px 0 0;
        color: #b9c8da;
        font-size: 1rem;
    }

    .kpi {
        min-height: 145px;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid var(--border);
        background: linear-gradient(145deg, rgba(15,36,60,.96), rgba(8,22,39,.96));
        box-shadow: 0 12px 35px rgba(0,0,0,.20);
        position: relative;
        overflow: hidden;
    }

    .kpi:after {
        content: "";
        position: absolute;
        width: 90px;
        height: 90px;
        border-radius: 50%;
        left: -30px;
        top: -35px;
        background: rgba(59,130,246,.12);
    }

    .kpi .label {
        color: var(--muted);
        font-size: .92rem;
        margin-bottom: 7px;
    }

    .kpi .value {
        color: #fff;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
    }

    .kpi .sub {
        color: #9fb0c4;
        font-size: .78rem;
        margin-top: 8px;
    }

    .section-title {
        margin: 26px 0 10px;
        font-size: 1.28rem;
        font-weight: 800;
        color: #ffffff;
    }

    .story-card {
        padding: 18px 20px;
        border-radius: 18px;
        border: 1px solid var(--border);
        background: rgba(13,27,45,.82);
        min-height: 145px;
    }

    .story-card .num {
        font-size: 1.5rem;
        font-weight: 800;
        color: #67e8f9;
    }

    .story-card .title {
        color: #e2e8f0;
        font-weight: 700;
        margin: 5px 0;
    }

    .story-card .body {
        color: #9fb0c4;
        font-size: .88rem;
        line-height: 1.8;
    }

    .recommendation {
        border-right: 4px solid var(--green);
        padding: 14px 18px;
        margin: 10px 0;
        background: rgba(16,185,129,.07);
        border-radius: 12px;
        color: #dcefe9;
        line-height: 1.9;
    }

    .warning {
        border-right: 4px solid var(--orange);
        padding: 14px 18px;
        margin: 10px 0;
        background: rgba(249,115,22,.07);
        border-radius: 12px;
        color: #f5e6d9;
        line-height: 1.9;
    }

    .small-note {
        color: #8496ab;
        font-size: .78rem;
        line-height: 1.8;
    }

    .stDownloadButton button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid rgba(34,211,238,.3);
        background: rgba(34,211,238,.08);
        color: #dffaff;
    }

    div[data-baseweb="select"] > div {
        background-color: #0c1b2e !important;
        border-color: rgba(148,163,184,.18) !important;
    }

    .stMetric {
        direction: rtl;
    }

    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 3) الثوابت + قاموس الحقول
# ============================================================
DATA_FILE = Path(__file__).resolve().parent / "hr_master_clean.csv"

# ترتيب الأعمدة الفعلي المكتشف في الملف.
# القراءة header=None ضرورية لأن الصف الأول في الملف هو سجل بيانات وليس ترويسة.
COLUMN_MAP = {
    0: "enrollee_id",
    1: "data_source",
    2: "target",
    3: "target_flag_engineered",
    4: "sample_weight",
    5: "city",
    6: "city_development_index",
    7: "gender",
    8: "relevant_experience",
    9: "relevant_experience_flag",
    10: "enrolled_university",
    11: "education_level",
    12: "education_level_code",
    13: "major_discipline",
    14: "experience_raw",
    15: "experience_numeric_a",
    16: "experience_numeric_b",
    17: "experience_band",
    18: "experience_code",
    19: "company_size",
    20: "company_size_label",
    21: "company_size_code",
    22: "company_type_code",
    23: "company_type",
    24: "employment_status_engineered",
    25: "last_new_job",
    26: "last_new_job_numeric_a",
    27: "last_new_job_numeric_b",
    28: "job_change_flag_engineered",
    29: "training_hours",
    30: "city_development_band",
    31: "education_level_code_2",
    32: "major_stem_flag",
    33: "major_other_flag",
    34: "major_no_major_flag",
    35: "major_humanities_flag",
    36: "major_business_flag",
    37: "major_arts_flag",
    38: "major_not_applicable_flag",
    39: "major_unknown_flag",
    40: "company_size_large_flag",
    41: "company_size_small_flag",
    42: "company_size_unknown_flag",
    43: "experience_code_2",
    44: "last_new_job_code_2",
    45: "likely_unemployed_flag",
    46: "partial_company_info_flag",
}

AR_LABELS = {
    "data_source": "مصدر البيانات",
    "gender": "الجنس",
    "experience_band": "نوع/فئة الخبرة",
    "education_level": "مستوى التعليم",
    "major_discipline": "التخصص الأكاديمي",
    "company_size": "حجم الشركة",
    "company_type": "نوع الشركة",
    "enrolled_university": "حالة الالتحاق الجامعي",
    "last_new_job": "الفترة منذ آخر تغيير وظيفي",
}

# ============================================================
# 4) تحميل وتنظيف البيانات
# ============================================================
@st.cache_data(show_spinner=False)
def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"لم يتم العثور على الملف: {DATA_FILE}\n"
            "ضع hr_master_clean.csv في نفس مجلد app.py."
        )

    raw = pd.read_csv(DATA_FILE, header=None, low_memory=False)

    if raw.shape[1] < 47:
        raise ValueError(
            f"الملف يحتوي على {raw.shape[1]} عموداً فقط، بينما البنية المتوقعة تحتوي على 47 عموداً."
        )

    # إذا كان هناك أعمدة زائدة لا نحتاجها، نحتفظ بالبنية المعروفة فقط.
    raw = raw.iloc[:, :47].copy()
    raw.columns = [COLUMN_MAP[i] for i in range(47)]

    # الأنواع
    for c in [
        "target",
        "city_development_index",
        "experience_numeric_a",
        "experience_numeric_b",
        "training_hours",
        "last_new_job_numeric_a",
        "last_new_job_numeric_b",
    ]:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")

    raw["target"] = raw["target"].astype("Float64")

    # توحيد النصوص
    text_cols = raw.select_dtypes(include=["object"]).columns
    for c in text_cols:
        raw[c] = raw[c].astype("string").str.strip()
        raw[c] = raw[c].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "NaN": pd.NA,
                "NULL": pd.NA,
            }
        )

    # تسميات عربية إضافية
    raw["مصدر"] = raw["data_source"].map({"train": "تدريب", "test": "اختبار"}).fillna(
        raw["data_source"]
    )
    raw["الجنس"] = raw["gender"].fillna("Unknown").replace({"Unknown": "غير معروف"})
    raw["الخبرة"] = raw["experience_band"].fillna(raw["experience_raw"]).fillna("غير معروف")
    raw["التعليم"] = raw["education_level"].fillna("غير معروف")
    raw["التخصص"] = raw["major_discipline"].fillna("غير معروف")
    raw["حجم_الشركة"] = raw["company_size"].fillna("غير معروف")
    raw["نوع_الشركة"] = raw["company_type"].fillna("غير معروف")

    # الخبرة الرقمية: نستخدم العمود الهندسي المتاح ثم نستنتجها من الفئة عند الحاجة.
    exp = raw["experience_numeric_a"].copy()
    exp_fallback = raw["experience_numeric_b"].copy()
    exp = exp.fillna(exp_fallback)

    exp_map = {
        "<1 yr": 0.5,
        "1-2 yrs": 1.5,
        "3-5 yrs": 4,
        "6-10 yrs": 8,
        "11-15 yrs": 13,
        "16-20 yrs": 18,
        ">20 yrs": 21,
    }
    raw["experience_years"] = exp
    missing_exp = raw["experience_years"].isna()
    raw.loc[missing_exp, "experience_years"] = raw.loc[missing_exp, "experience_raw"].map(exp_map)

    # متغيرات الهدف
    raw["target_label"] = raw["target"].map({0.0: "مستقر/لا يترك", 1.0: "مرشح لترك الوظيفة"})
    raw["target_label"] = raw["target_label"].fillna("غير متاح")

    # مؤشر تغيير الوظيفة
    raw["job_change_index"] = pd.to_numeric(raw["last_new_job_numeric_a"], errors="coerce")
    raw["job_change_index"] = raw["job_change_index"].fillna(
        pd.to_numeric(raw["last_new_job_numeric_b"], errors="coerce")
    )

    return raw


@st.cache_data(show_spinner=False)
def train_risk_model(df):
    """
    نموذج لوجستي بسيط ومفسر لتقدير احتمال target=1.
    يُدرّب فقط على سجلات train ذات target معروف.
    إذا لم تتوفر scikit-learn أو حدثت مشكلة، نعيد None.
    """
    try:
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        train = df[(df["data_source"] == "train") & df["target"].notna()].copy()
        if train["target"].nunique() < 2 or len(train) < 100:
            return None

        features = [
            "city_development_index",
            "gender",
            "relevant_experience",
            "enrolled_university",
            "education_level",
            "major_discipline",
            "experience_raw",
            "company_size",
            "company_type",
            "last_new_job",
            "training_hours",
        ]

        X = train[features]
        y = train["target"].astype(int)

        numeric_features = ["city_development_index", "training_hours"]
        categorical_features = [c for c in features if c not in numeric_features]

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "num",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    numeric_features,
                ),
                (
                    "cat",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    categorical_features,
                ),
            ]
        )

        model = Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=700,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        )

        model.fit(X, y)
        return model, features

    except Exception:
        return None


try:
    data = load_data()
except Exception as e:
    st.error(f"تعذر تحميل البيانات: {e}")
    st.stop()

# ============================================================
# 5) العنوان
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>🧠 HR Intelligence — تحليلات علماء البيانات</h1>
        <p>
            منصة تفاعلية لتحليل الاستقرار الوظيفي، عوامل تغيير الوظيفة،
            أثر الشركة والخبرة، وتقدير مخاطر التسرب الوظيفي.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 6) الشريط الجانبي — الفلاتر
# ============================================================
st.sidebar.markdown("## 🎛️ مركز التحكم")
st.sidebar.caption("جميع الفلاتر تعمل لحظياً على المؤشرات والرسوم والتحليلات.")

def options_for(col, label_map=None):
    vals = data[col].dropna().astype(str).unique().tolist()
    vals = sorted(vals)
    if label_map:
        return [label_map.get(v, v) for v in vals]
    return vals

source_options = ["الكل"] + sorted(data["مصدر"].dropna().unique().tolist())
gender_options = ["الكل"] + sorted(data["الجنس"].dropna().unique().tolist())
exp_options = ["الكل"] + sorted(data["الخبرة"].dropna().unique().tolist())
edu_options = ["الكل"] + sorted(data["التعليم"].dropna().unique().tolist())
major_options = ["الكل"] + sorted(data["التخصص"].dropna().unique().tolist())
size_options = ["الكل"] + sorted(data["حجم_الشركة"].dropna().unique().tolist())
type_options = ["الكل"] + sorted(data["نوع_الشركة"].dropna().unique().tolist())

selected_source = st.sidebar.multiselect(
    "📁 مصدر البيانات", source_options, default=["الكل"]
)
selected_gender = st.sidebar.multiselect(
    "👤 الجنس", gender_options, default=["الكل"]
)
selected_exp = st.sidebar.multiselect(
    "🧠 نوع الخبرة", exp_options, default=["الكل"]
)
selected_edu = st.sidebar.multiselect(
    "🎓 مستوى التعليم", edu_options, default=["الكل"]
)
selected_major = st.sidebar.multiselect(
    "🔬 التخصص الأكاديمي", major_options, default=["الكل"]
)

with st.sidebar.expander("🏢 فلاتر متقدمة", expanded=False):
    selected_size = st.multiselect(
        "حجم الشركة", size_options, default=["الكل"]
    )
    selected_type = st.multiselect(
        "نوع الشركة", type_options, default=["الكل"]
    )

    city_min, city_max = st.slider(
        "مؤشر تنمية المدينة",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.01,
    )

    training_min, training_max = st.slider(
        "ساعات التدريب",
        min_value=0,
        max_value=int(max(1, data["training_hours"].max(skipna=True))),
        value=(0, int(max(1, data["training_hours"].max(skipna=True)))),
    )

def apply_filter(frame, col, selections):
    if not selections or "الكل" in selections:
        return frame
    return frame[frame[col].astype(str).isin(selections)]

filtered = data.copy()
filtered = apply_filter(filtered, "مصدر", selected_source)
filtered = apply_filter(filtered, "الجنس", selected_gender)
filtered = apply_filter(filtered, "الخبرة", selected_exp)
filtered = apply_filter(filtered, "التعليم", selected_edu)
filtered = apply_filter(filtered, "التخصص", selected_major)
filtered = apply_filter(filtered, "حجم_الشركة", selected_size)
filtered = apply_filter(filtered, "نوع_الشركة", selected_type)
filtered = filtered[
    filtered["city_development_index"].between(city_min, city_max, inclusive="both")
]
filtered = filtered[
    filtered["training_hours"].fillna(training_min).between(
        training_min, training_max, inclusive="both"
    )
].copy()

if filtered.empty:
    st.warning("لا توجد سجلات تطابق مجموعة الفلاتر الحالية. وسّع الفلاتر لرؤية النتائج.")
    st.stop()

# ============================================================
# 7) نموذج المخاطر
# ============================================================
model_bundle = train_risk_model(data)

if model_bundle is not None:
    model, model_features = model_bundle
    try:
        filtered["predicted_leave_probability"] = (
            model.predict_proba(filtered[model_features])[:, 1] * 100
        )
    except Exception:
        filtered["predicted_leave_probability"] = np.nan
else:
    # fallback شفاف عند عدم توفر sklearn
    risk = pd.Series(35.0, index=filtered.index)
    risk += np.where(filtered["city_development_index"].fillna(.7) < .65, 10, 0)
    risk += np.where(filtered["relevant_experience"].eq("No relevent experience"), 8, 0)
    risk += np.where(filtered["last_new_job"].isin(["never", ">4"]), 5, 0)
    risk += np.where(filtered["company_size"].isin(["<10", "10-49"]), 7, 0)
    risk += np.where(filtered["experience_years"].fillna(5) < 2, 6, 0)
    filtered["predicted_leave_probability"] = risk.clip(0, 95)

# ============================================================
# 8) KPIs
# ============================================================
labeled = filtered[filtered["target"].notna()].copy()
target_rate = labeled["target"].mean() * 100 if not labeled.empty else np.nan
avg_exp = filtered["experience_years"].mean()
avg_risk = filtered["predicted_leave_probability"].mean()
avg_city_index = filtered["city_development_index"].mean()

c1, c2, c3, c4, c5 = st.columns(5)

def kpi(col, label, value, sub):
    col.markdown(
        f"""
        <div class="kpi">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

kpi(c1, "👥 إجمالي السجلات", f"{len(filtered):,}", "بعد تطبيق الفلاتر")
kpi(c2, "🚪 معدل الترك المرصود", f"{target_rate:.1f}%" if not np.isnan(target_rate) else "—",
    "محسوب على السجلات ذات target معروف")
kpi(c3, "⚠️ احتمال الترك التقديري", f"{avg_risk:.1f}%",
    "نموذج لوجستي مدرّب على بيانات التدريب" if model_bundle else "مؤشر بديل عند غياب sklearn")
kpi(c4, "🧠 متوسط الخبرة", f"{avg_exp:.1f} سنة" if not np.isnan(avg_exp) else "—",
    "تقريب مبني على الحقول المتاحة")
kpi(c5, "🏙️ متوسط تنمية المدينة", f"{avg_city_index:.3f}" if not np.isnan(avg_city_index) else "—",
    "City Development Index")

# ============================================================
# 9) توزيع الهدف
# ============================================================
st.markdown('<div class="section-title">📌 لوحة الاستقرار الوظيفي</div>', unsafe_allow_html=True)

ch1, ch2 = st.columns(2)

with ch1:
    if not labeled.empty:
        target_counts = (
            labeled["target_label"]
            .value_counts()
            .rename_axis("الحالة")
            .reset_index(name="العدد")
        )
        fig = px.pie(
            target_counts,
            names="الحالة",
            values="العدد",
            hole=0.58,
            title="توزيع الهدف — السجلات ذات التصنيف المعروف",
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Cairo", color="#e5eef8"),
            title_font_size=17,
            legend=dict(orientation="h", y=-0.08),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد سجلات تدريب ذات target معروف ضمن الفلاتر.")

with ch2:
    split_counts = (
        filtered["مصدر"].value_counts()
        .rename_axis("المصدر")
        .reset_index(name="العدد")
    )
    fig = px.bar(
        split_counts,
        x="المصدر",
        y="العدد",
        text_auto=True,
        title="حجم بيانات التدريب والاختبار",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Cairo", color="#e5eef8"),
        title_font_size=17,
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 10) أثر حجم ونوع الشركة
# ============================================================
st.markdown('<div class="section-title">🏢 أثر الشركة على الاستقرار الوظيفي</div>', unsafe_allow_html=True)

company_labeled = filtered[filtered["target"].notna()].copy()

cc1, cc2 = st.columns(2)

with cc1:
    if not company_labeled.empty:
        size_analysis = (
            company_labeled.groupby("حجم_الشركة", dropna=False)
            .agg(
                معدل_الترك=("target", "mean"),
                العدد=("target", "size"),
            )
            .reset_index()
        )
        size_analysis["معدل_الترك"] *= 100
        size_analysis = size_analysis.sort_values("معدل_الترك", ascending=False)

        fig = px.bar(
            size_analysis,
            x="حجم_الشركة",
            y="معدل_الترك",
            text=size_analysis["معدل_الترك"].round(1).astype(str) + "%",
            hover_data=["العدد"],
            title="معدل الترك حسب حجم الشركة",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            yaxis_title="معدل الترك (%)",
            xaxis_title="حجم الشركة",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Cairo", color="#e5eef8"),
        )
        st.plotly_chart(fig, use_container_width=True)

with cc2:
    if not company_labeled.empty:
        type_analysis = (
            company_labeled.groupby("نوع_الشركة", dropna=False)
            .agg(
                معدل_الترك=("target", "mean"),
                العدد=("target", "size"),
            )
            .reset_index()
        )
        type_analysis["معدل_الترك"] *= 100
        type_analysis = type_analysis.sort_values("معدل_الترك", ascending=False)

        fig = px.bar(
            type_analysis,
            x="نوع_الشركة",
            y="معدل_الترك",
            text=type_analysis["معدل_الترك"].round(1).astype(str) + "%",
            hover_data=["العدد"],
            title="معدل الترك حسب نوع الشركة",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            yaxis_title="معدل الترك (%)",
            xaxis_title="نوع الشركة",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Cairo", color="#e5eef8"),
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 11) الخبرة + التعليم + التخصص
# ============================================================
st.markdown('<div class="section-title">🧬 العوامل الفردية والمهنية</div>', unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3)

with fc1:
    if not company_labeled.empty:
        exp_analysis = (
            company_labeled.groupby("الخبرة", dropna=False)["target"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "معدل_الترك", "count": "العدد"})
        )
        exp_analysis["معدل_الترك"] *= 100
        exp_analysis = exp_analysis.sort_values("معدل_الترك", ascending=False)

        fig = px.bar(
            exp_analysis,
            x="الخبرة",
            y="معدل_الترك",
            hover_data=["العدد"],
            text=exp_analysis["معدل_الترك"].round(1).astype(str) + "%",
            title="معدل الترك حسب الخبرة",
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="معدل الترك (%)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Cairo", color="#e5eef8"),
        )
        st.plotly_chart(fig, use_container_width=True)

with fc2:
    if not company_labeled.empty:
        edu_analysis = (
            company_labeled.groupby("التعليم", dropna=False)["target"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "معدل_الترك", "count": "العدد"})
        )
        edu_analysis["معدل_الترك"] *= 100

        fig = px.bar(
            edu_analysis.sort_values("معدل_الترك", ascending=False),
            x="التعليم",
            y="معدل_الترك",
            hover_data=["العدد"],
            text=edu_analysis["معدل_الترك"].round(1).astype(str) + "%",
            title="معدل الترك حسب التعليم",
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="معدل الترك (%)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Cairo", color="#e5eef8"),
        )
        st.plotly_chart(fig, use_container_width=True)

with fc3:
    if not company_labeled.empty:
        major_analysis = (
            company_labeled.groupby("التخصص", dropna=False)["target"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "معدل_الترك", "count": "العدد"})
        )
        major_analysis["معدل_الترك"] *= 100
        major_analysis = major_analysis.sort_values("معدل_الترك", ascending=False).head(10)

        fig = px.bar(
            major_analysis,
            x="معدل_الترك",
            y="التخصص",
            orientation="h",
            hover_data=["العدد"],
            text=major_analysis["معدل_الترك"].round(1).astype(str) + "%",
            title="أعلى التخصصات حسب معدل الترك",
        )
        fig.update_layout(
            xaxis_title="معدل الترك (%)",
            yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Cairo", color="#e5eef8"),
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 12) العلاقة بين تنمية المدينة والترك
# ============================================================
st.markdown('<div class="section-title">🏙️ السياق الجغرافي والتنموي</div>', unsafe_allow_html=True)

if not company_labeled.empty:
    scatter_df = company_labeled[
        ["city", "city_development_index", "experience_years", "target", "company_size"]
    ].dropna(subset=["city_development_index", "target"])

    if len(scatter_df) > 0:
        # عينة للعرض إذا كان عدد النقاط ضخماً
        plot_df = scatter_df.sample(min(6000, len(scatter_df)), random_state=42)

        fig = px.scatter(
            plot_df,
            x="city_development_index",
            y="experience_years",
            color="target",
            size="target",
            hover_data=["city", "company_size"],
            labels={
                "city_development_index": "مؤشر تنمية المدينة",
                "experience_years": "الخبرة التقريبية (سنوات)",
                "target": "الهدف",
            },
            title="تنمية المدينة × الخبرة × الهدف",
            opacity=0.62,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Cairo", color="#e5eef8"),
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 13) التحليل الذكي / سرد قصة البيانات
# ============================================================
st.markdown('<div class="section-title">📖 قصة البيانات — ماذا تقول الأرقام؟</div>', unsafe_allow_html=True)

if not company_labeled.empty:
    # أكبر فجوة بين مجموعات الشركة
    size_stats = (
        company_labeled.groupby("حجم_الشركة")["target"]
        .agg(["mean", "count"])
        .reset_index()
    )
    size_stats["mean"] *= 100
    size_stats = size_stats[size_stats["count"] >= 30]

    type_stats = (
        company_labeled.groupby("نوع_الشركة")["target"]
        .agg(["mean", "count"])
        .reset_index()
    )
    type_stats["mean"] *= 100
    type_stats = type_stats[type_stats["count"] >= 30]

    exp_stats = (
        company_labeled.groupby("الخبرة")["target"]
        .agg(["mean", "count"])
        .reset_index()
    )
    exp_stats["mean"] *= 100
    exp_stats = exp_stats[exp_stats["count"] >= 30]

    def stat_sentence(df_, label_col, value_col="mean"):
        if df_.empty:
            return "لا توجد عينة كافية."
        hi = df_.sort_values(value_col, ascending=False).iloc[0]
        lo = df_.sort_values(value_col, ascending=True).iloc[0]
        return (
            f"الفئة ذات المعدل الأعلى في العينة هي «{hi[label_col]}» "
            f"({hi[value_col]:.1f}%)، بينما الأدنى «{lo[label_col]}» "
            f"({lo[value_col]:.1f}%)."
        )

    s1, s2, s3 = st.columns(3)

    with s1:
        st.markdown(
            f"""
            <div class="story-card">
                <div class="num">01</div>
                <div class="title">أثر حجم الشركة</div>
                <div class="body">{stat_sentence(size_stats, "حجم_الشركة")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s2:
        st.markdown(
            f"""
            <div class="story-card">
                <div class="num">02</div>
                <div class="title">أثر نوع الشركة</div>
                <div class="body">{stat_sentence(type_stats, "نوع_الشركة")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with s3:
        st.markdown(
            f"""
            <div class="story-card">
                <div class="num">03</div>
                <div class="title">الخبرة المهنية</div>
                <div class="body">{stat_sentence(exp_stats, "الخبرة")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="small-note">
        ملاحظة منهجية: هذه المقارنات وصفية وليست دليلاً على السببية. ارتفاع معدل الترك في فئة معينة
        لا يعني أن المتغير وحده تسبب في ترك الوظيفة؛ ينبغي دمج هذه النتائج مع سياق التعويضات،
        فرص التطور، طبيعة الدور، وسياسات الاحتفاظ بالمواهب.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 14) التوصيات الاستراتيجية
# ============================================================
st.markdown('<div class="section-title">🎯 التوصيات الاستراتيجية لصنّاع القرار</div>', unsafe_allow_html=True)

if not company_labeled.empty:
    overall = company_labeled["target"].mean() * 100

    # توصيات مبنية على الأنماط المرصودة في الفلاتر الحالية.
    low_dev_rate = company_labeled.loc[
        company_labeled["city_development_index"] < 0.65, "target"
    ].mean() * 100

    no_exp_rate = company_labeled.loc[
        company_labeled["relevant_experience"].eq("No relevent experience"), "target"
    ].mean() * 100

    early_career = company_labeled.loc[
        company_labeled["experience_years"].fillna(99) < 2, "target"
    ].mean() * 100

    rec1 = (
        "فعّل برنامجاً مبكراً للاحتفاظ بالمواهب الجديدة، مع مراجعات مهنية خلال أول 6–12 شهراً، "
        "إذا كانت فئة الخبرة القصيرة تظهر معدل ترك مرتفعاً في العينة."
        if not np.isnan(early_career) and early_career > overall
        else
        "استمر في قياس تجربة الموظف حسب شرائح الخبرة بدلاً من استخدام سياسة احتفاظ واحدة لجميع الموظفين."
    )

    rec2 = (
        "أدخل الموقع/بيئة المدينة كمتغير في تخطيط التوظيف والاحتفاظ؛ إذا كانت المدن ذات مؤشر تنمية منخفض "
        "تظهر معدلات ترك أعلى، فاختبر العمل الهجين، التعويضات المحلية، أو مسارات التطور المرتبطة بالموقع."
        if not np.isnan(low_dev_rate) and low_dev_rate > overall
        else
        "لا تعتمد على مؤشر المدينة وحده؛ اربطه بمؤشرات التعويض، التنقل، ونوعية الدور قبل اتخاذ قرارات الاحتفاظ."
    )

    rec3 = (
        "أنشئ مسارات onboarding وتطوير واضحة للموظفين الذين لا يملكون خبرة سابقة ذات صلة، "
        "مع قياس الانتقال من أول وظيفة إلى الاستقرار."
        if not np.isnan(no_exp_rate) and no_exp_rate > overall
        else
        "استعمل الخبرة ذات الصلة كعامل تقسيم في برامج التطوير، مع متابعة معدلات الترك لكل شريحة."
    )

    st.markdown(f'<div class="recommendation"><b>القاعدة الذهبية الأولى:</b> {rec1}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="recommendation"><b>القاعدة الذهبية الثانية:</b> {rec2}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="warning"><b>تنبيه لصانع القرار:</b> {rec3} لا تُحوّل الارتباطات الإحصائية إلى قرارات سببية قبل اختبارها.</div>', unsafe_allow_html=True)

# ============================================================
# 15) جدول المخاطر الأعلى
# ============================================================
st.markdown('<div class="section-title">🚨 الحالات ذات الاحتمال التقديري الأعلى</div>', unsafe_allow_html=True)

risk_cols = [
    "enrollee_id",
    "مصدر",
    "الجنس",
    "الخبرة",
    "التعليم",
    "التخصص",
    "حجم_الشركة",
    "نوع_الشركة",
    "last_new_job",
    "city_development_index",
    "predicted_leave_probability",
    "target_label",
]

risk_view = filtered[risk_cols].copy()
risk_view = risk_view.sort_values(
    "predicted_leave_probability", ascending=False
).head(25)

risk_view = risk_view.rename(
    columns={
        "enrollee_id": "معرّف",
        "مصدر": "المصدر",
        "الجنس": "الجنس",
        "الخبرة": "الخبرة",
        "التعليم": "التعليم",
        "التخصص": "التخصص",
        "حجم_الشركة": "حجم الشركة",
        "نوع_الشركة": "نوع الشركة",
        "last_new_job": "آخر تغيير وظيفي",
        "city_development_index": "مؤشر المدينة",
        "predicted_leave_probability": "احتمال الترك التقديري %",
        "target_label": "الهدف المرصود",
    }
)

risk_view["احتمال الترك التقديري %"] = risk_view[
    "احتمال الترك التقديري %"
].round(1)
risk_view["مؤشر المدينة"] = risk_view["مؤشر المدينة"].round(3)

st.dataframe(
    risk_view,
    use_container_width=True,
    hide_index=True,
)

# ============================================================
# 16) تصدير النتائج
# ============================================================
st.markdown('<div class="section-title">⬇️ تصدير التحليل</div>', unsafe_allow_html=True)

export_df = filtered.copy()
csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "📥 تنزيل البيانات المفلترة + مؤشرات المخاطر بصيغة CSV",
    data=csv_bytes,
    file_name="hr_dashboard_filtered.csv",
    mime="text/csv",
)

# ============================================================
# 17) تذييل منهجي
# ============================================================
st.markdown(
    """
    <div class="small-note" style="margin-top:25px; text-align:center;">
        HR Intelligence Dashboard • Streamlit + Plotly •
        التحليل الوصفي لا يثبت السببية، واحتمال الترك التقديري هو مخرج نموذجي وليس حكماً نهائياً على الموظف.
    </div>
    """,
    unsafe_allow_html=True,
)
