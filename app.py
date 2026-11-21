import tempfile
from pathlib import Path
import streamlit as st

from pdf_processing.reader import read_pdf  # type: ignore
from pdf_processing.parser import extract_facts  # type: ignore
from inference_engine.engine import run_inference  # type: ignore
from inference_engine.explanation import build_explanation_report  # type: ignore

st.set_page_config(page_title="CBC Expert AI", page_icon="🩸", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

* { font-family: 'Cairo', sans-serif !important; }
.stApp { background-color: #fdf8f8; direction: rtl; text-align: right; }
.block-container { max-width: 1080px; padding-top: 1.8rem; padding-bottom: 3rem; }
#MainMenu, footer, header { visibility: hidden; }

/* البانر الأحمر العلوي */
.red-banner {
    background: linear-gradient(135deg, #7f1d1d 0%, #b91c1c 55%, #dc2626 100%);
    padding: 30px 32px;
    border-radius: 20px;
    color: #ffffff;
    box-shadow: 0 12px 28px rgba(185, 28, 28, 0.22);
    margin-bottom: 22px;
    text-align: right;
}
.red-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.18);
    padding: 4px 14px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 8px;
}
.red-banner h1 { color: #ffffff !important; margin: 0; font-size: 1.9rem; font-weight: 800; }
.red-banner p { color: #fee2e2 !important; margin: 6px 0 0; font-size: 0.96rem; }

/* مربع رفع الملف */
div[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 2px dashed #f87171;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 4px 14px rgba(185, 28, 28, 0.05);
}
div[data-testid="stFileUploader"] section { direction: rtl; text-align: right; }

/* شريط بيانات المريض */
.info-strip {
    background: #ffffff;
    border: 1px solid #fecaca;
    border-right: 5px solid #dc2626;
    border-radius: 14px;
    padding: 14px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 18px;
}
.red-pill {
    background: #fef2f2;
    color: #b91c1c;
    border: 1px solid #fecaca;
    padding: 5px 14px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 700;
}

/* بطاقات المؤشرات الأربعة */
.cards-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 18px 0;
}
.blood-card {
    background: #ffffff;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #fee2e2;
    border-top: 4px solid #dc2626;
    box-shadow: 0 4px 12px rgba(153, 27, 27, 0.05);
    text-align: right;
}
.blood-label { color: #7f1d1d; font-size: 0.88rem; font-weight: 700; }
.blood-val { color: #1f2937; font-size: 1.75rem; font-weight: 800; margin: 4px 0; }
.blood-unit { color: #dc2626; font-size: 0.78rem; font-weight: 600; }

/* بطاقات التشخيص */
.result-box {
    padding: 16px 20px;
    border-radius: 14px;
    font-weight: 800;
    font-size: 1.05rem;
    margin-bottom: 16px;
}
.res-urgent { background: #fef2f2; border: 1px solid #fca5a5; border-right: 6px solid #dc2626; color: #991b1b; }
.res-warning { background: #fffbeb; border: 1px solid #fcd34d; border-right: 6px solid #d97706; color: #92400e; }
.res-info { background: #fff1f2; border: 1px solid #fecdd3; border-right: 6px solid #e11d48; color: #9f1239; }
.res-normal { background: #f0fdf4; border: 1px solid #86efac; border-right: 6px solid #16a34a; color: #166534; }

.rule-card {
    background: #ffffff;
    border: 1px solid #fecaca;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}
.rule-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.rule-badge {
    background: #fef2f2;
    color: #991b1b;
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
}
.rule-title { color: #111827; font-size: 1.05rem; font-weight: 800; margin: 4px 0; }
.rule-text { color: #4b5563; font-size: 0.93rem; margin: 0; }

/* خطوات البداية */
.guide-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px; }
.guide-item {
    background: #ffffff;
    padding: 22px 18px;
    border-radius: 16px;
    border: 1px solid #fee2e2;
    text-align: center;
}
.guide-num {
    width: 36px; height: 36px; line-height: 36px;
    background: #fee2e2; color: #b91c1c;
    border-radius: 50%; font-weight: 800; margin: 0 auto 10px;
}
.guide-item h4 { color: #7f1d1d; margin: 0 0 6px; font-weight: 700; }
.guide-item p { color: #6b7280; font-size: 0.87rem; margin: 0; }

/* التبويبات باللون الأحمر */
.stTabs [data-baseweb="tab-list"] { gap: 10px; direction: rtl; margin-top: 8px; }
.stTabs [data-baseweb="tab"] {
    background: #ffffff; border-radius: 10px; padding: 10px 20px;
    border: 1px solid #fecaca; font-weight: 700; color: #7f1d1d;
}
.stTabs [aria-selected="true"] {
    background: #b91c1c !important; color: #ffffff !important; border-color: #b91c1c !important;
}
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown("""
<div class="red-banner">
    <div class="red-badge">🩸 نظام خبير طبي لتحليل الدم • CBC Expert System</div>
    <h1>النظام الخبير لتحليل صورة الدم الكاملة (CBC)</h1>
    <p>ارفع ملف التحليل (PDF) وسيقوم النظام باستخراج القيم وتشغيل 30 قاعدة طبية لتقديم التشخيص والتفسير فوراً.</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 اضغط هنا لاختيار تقرير تحليل الدم (PDF) أو اسحبه إلى المربع", type=["pdf"])

if uploaded_file is None:
    st.markdown("""
    <div class="guide-grid">
        <div class="guide-item">
            <div class="guide-num">1</div>
            <h4>ارفع التقرير</h4>
            <p>اختر ملف فحص الدم بصيغة PDF من جهازك بضغطة واحدة.</p>
        </div>
        <div class="guide-item">
            <div class="guide-num">2</div>
            <h4>قراءة الفحوصات</h4>
            <p>يستخرج النظام 17 مؤشراً طبياً مع العمر والجنس تلقائياً.</p>
        </div>
        <div class="guide-item">
            <div class="guide-num">3</div>
            <h4>التشخيص والتفسير</h4>
            <p>يعرض لك النتيجة الطبية والقواعد التي تم تفعيلها بوضوح.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = Path(tmp.name)

    try:
        with st.spinner("🩸 جاري تحليل التقرير وتشغيل القواعد الطبية..."):
            raw_facts = extract_facts(read_pdf(tmp_path))

        if not raw_facts:
            st.error("⚠️ لم يتم العثور على قيم CBC واضحة في الملف. تأكد أن الملف تقرير نصي وليس صورة.")
        else:
            inference_out = run_inference(raw_facts)
            report = build_explanation_report(inference_out)
            facts = inference_out["facts"]
            statuses = inference_out["statuses"]

            sex_ar = "ذكر" if facts.get("sex") == "male" else ("أنثى" if facts.get("sex") == "female" else "غير محدد")
            age_ar = f"{facts.get('age')} سنة" if facts.get("age") is not None else "غير محدد"

            st.markdown(f"""
            <div class="info-strip">
                <div><b>👤 الجنس:</b> {sex_ar} &nbsp;|&nbsp; <b>🎂 العمر:</b> {age_ar} &nbsp;|&nbsp; <b>📄 الملف:</b> {uploaded_file.name}</div>
                <div class="red-pill">✓ تم فحص {inference_out['checked_count']} قاعدة • تفعيل {inference_out['fired_count']} قاعدة</div>
            </div>
            """, unsafe_allow_html=True)

            hb_val = facts.get("hb") if facts.get("hb") is not None else "—"
            wbc_val = facts.get("wbc") if facts.get("wbc") is not None else "—"
            plt_val = facts.get("platelets") if facts.get("platelets") is not None else "—"
            rbc_val = facts.get("rbc") if facts.get("rbc") is not None else "—"

            st.markdown(f"""
            <div class="cards-row">
                <div class="blood-card">
                    <div class="blood-label">🩸 الهيموجلوبين (Hb)</div>
                    <div class="blood-val">{hb_val}</div>
                    <div class="blood-unit">g/dL</div>
                </div>
                <div class="blood-card">
                    <div class="blood-label">🛡️ كريات بيضاء (WBC)</div>
                    <div class="blood-val">{wbc_val}</div>
                    <div class="blood-unit">×10⁹/L</div>
                </div>
                <div class="blood-card">
                    <div class="blood-label">🩹 الصفائح (Platelets)</div>
                    <div class="blood-val">{plt_val}</div>
                    <div class="blood-unit">×10⁹/L</div>
                </div>
                <div class="blood-card">
                    <div class="blood-label">🔴 كريات حمراء (RBC)</div>
                    <div class="blood-val">{rbc_val}</div>
                    <div class="blood-unit">×10¹²/L</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs([
                "🩺 النتيجة والتشخيص",
                "📋 جدول الفحوصات الـ 17",
                "⚙️ مسار الاستدلال"
            ])

            with tab1:
                box_cls = f"res-{report['overall_status']}"
                st.markdown(f'<div class="result-box {box_cls}">{report["overall_headline"]}</div>', unsafe_allow_html=True)

                findings = report["urgent_findings"] + report["warning_findings"] + report["info_findings"]
                if not findings:
                    st.success("✅ جميع الفحوصات المستخرجة ضمن المعدل الطبيعي ولا توجد مؤشرات مرضية.")
                else:
                    colors = {"urgent": "#dc2626", "warning": "#d97706", "info": "#e11d48"}
                    for item in findings:
                        c = colors.get(item["alert_type"], "#dc2626")
                        st.markdown(f"""
                        <div class="rule-card" style="border-right: 5px solid {c};">
                            <div class="rule-top">
                                <span style="font-weight:700; color:{c};">{item['alert_label']}</span>
                                <span class="rule-badge">القاعدة: {item['rule_id']}</span>
                            </div>
                            <div class="rule-title">{item['conclusion']}</div>
                            <p class="rule-text">{item['explanation']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                st.caption(report["disclaimer"])

            with tab2:
                icons = {
                    "طبيعي": "🟢 طبيعي",
                    "منخفض": "🔻 منخفض",
                    "مرتفع": "🔺 مرتفع",
                    "قيمة غير متوفرة": "⚪ غير متوفر",
                }
                rows = []
                for key, info in statuses.items():
                    r_min, r_max = info["reference"]
                    val_str = str(info["value"]) if info["value"] is not None else "—"
                    rows.append({
                        "الفحص": info["name"],
                        "الرمز": key.upper(),
                        "النتيجة": val_str,
                        "الوحدة": info["unit"],
                        "المعدل الطبيعي": f"{r_min} - {r_max}",
                        "التقييم": icons.get(info["status"], info["status"]),
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)

            with tab3:
                c1, c2, c3 = st.columns(3)
                c1.metric("إجمالي القواعد", f"{inference_out['total_rules']} قاعدة")
                c2.metric("القواعد المفحوصة", f"{inference_out['checked_count']} قاعدة")
                c3.metric("القواعد المفعّلة", f"{inference_out['fired_count']} قاعدة")

                st.info(f"🧠 {report['how_trace']}")

                trace = [
                    {
                        "رقم القاعدة": r["rule_id"],
                        "حالة الفحص": r["status"],
                        "النتيجة": r["conclusion"],
                    }
                    for r in inference_out["checked_rules"]
                ]
                st.dataframe(trace, use_container_width=True, hide_index=True)

    finally:
        tmp_path.unlink(missing_ok=True)
