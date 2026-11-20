import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "cbc_history.db"
REPORTS_DIR = BASE_DIR / "reports"


def init_db() -> None:
    """إنشاء قاعدة البيانات وجدول سجل التحاليل تلقائياً."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                file_name TEXT NOT NULL,
                sex TEXT,
                age INTEGER,
                hb REAL,
                wbc REAL,
                platelets REAL,
                rbc REAL,
                overall_headline TEXT,
                fired_rules TEXT
            )
        """)
        conn.commit()


def save_analysis_record(
    file_name: str,
    inference_out: Dict[str, Any],
    report: Dict[str, Any],
) -> int:
    """حفظ نتيجة التحليل في قاعدة البيانات SQLite."""
    init_db()
    facts = inference_out.get("facts", {})
    fired_ids = [r.get("rule_id", "") for r in inference_out.get("fired_rules", [])]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO analysis_records
            (created_at, file_name, sex, age, hb, wbc, platelets, rbc, overall_headline, fired_rules)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now_str,
                file_name,
                facts.get("sex"),
                facts.get("age"),
                facts.get("hb"),
                facts.get("wbc"),
                facts.get("platelets"),
                facts.get("rbc"),
                report.get("overall_headline", ""),
                json.dumps(fired_ids, ensure_ascii=False),
            ),
        )
        conn.commit()
        return cur.lastrowid or 0


def get_all_records() -> List[Dict[str, Any]]:
    """استرجاع جميع التحاليل المحفوظة مرتبة من الأحدث للأقدم."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM analysis_records ORDER BY id DESC"
        ).fetchall()

    results: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        try:
            rules_list = json.loads(item.get("fired_rules") or "[]")
            item["fired_rules"] = ", ".join(rules_list) if rules_list else "لا يوجد"
        except Exception:
            item["fired_rules"] = "—"
        results.append(item)
    return results


def generate_html_report(
    file_name: str,
    inference_out: Dict[str, Any],
    report: Dict[str, Any],
) -> tuple[str, Path]:
    """إنشاء تقرير طبي منسق وحفظه في مجلد reports وإرجاع محتواه للتحميل."""
    init_db()
    facts = inference_out.get("facts", {})
    statuses = inference_out.get("statuses", {})
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    sex_ar = "ذكر" if facts.get("sex") == "male" else ("أنثى" if facts.get("sex") == "female" else "غير محدد")
    age_ar = f"{facts.get('age')} سنة" if facts.get("age") is not None else "غير محدد"

    findings = report["urgent_findings"] + report["warning_findings"] + report["info_findings"]
    if findings:
        findings_html = "".join(
            f"<div class='card'><b>[{f['rule_id']}] {f['conclusion']}</b><p>{f['explanation']}</p></div>"
            for f in findings
        )
    else:
        findings_html = "<div class='card ok'>✅ جميع الفحوصات المستخرجة ضمن المعدل الطبيعي.</div>"

    rows_html = ""
    for key, info in statuses.items():
        r_min, r_max = info["reference"]
        val_str = str(info["value"]) if info["value"] is not None else "—"
        rows_html += f"<tr><td>{info['name']}</td><td>{key.upper()}</td><td>{val_str}</td><td>{info['unit']}</td><td>{r_min} - {r_max}</td><td>{info['status']}</td></tr>"

    html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>تقرير تحليل CBC - {file_name}</title>
<style>
body {{ font-family: Tahoma, Arial, sans-serif; background: #fff; color: #1f2937; padding: 28px; direction: rtl; }}
.header {{ background: #b91c1c; color: #fff; padding: 20px; border-radius: 12px; margin-bottom: 18px; }}
.meta {{ background: #fef2f2; border: 1px solid #fecaca; padding: 12px 16px; border-radius: 10px; margin-bottom: 18px; }}
.headline {{ background: #fff1f2; border-right: 5px solid #dc2626; padding: 14px; font-weight: bold; margin-bottom: 16px; }}
.card {{ border: 1px solid #fecaca; border-right: 4px solid #dc2626; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px; }}
.ok {{ border-right-color: #16a34a; background: #f0fdf4; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: right; }}
th {{ background: #b91c1c; color: #fff; }}
.footer {{ margin-top: 20px; font-size: 12px; color: #6b7280; }}
</style>
</head>
<body>
<div class="header"><h2>🩸 تقرير النظام الخبير لتحليل صورة الدم الكاملة (CBC)</h2><p>تاريخ التقرير: {now_str}</p></div>
<div class="meta"><b>الملف:</b> {file_name} &nbsp;|&nbsp; <b>الجنس:</b> {sex_ar} &nbsp;|&nbsp; <b>العمر:</b> {age_ar} &nbsp;|&nbsp; <b>القواعد المفعّلة:</b> {inference_out['fired_count']} من {inference_out['total_rules']}</div>
<div class="headline">{report['overall_headline']}</div>
<h3>التشخيص والتفسير الطبي</h3>
{findings_html}
<h3>جدول الفحوصات الـ 17</h3>
<table>
<thead><tr><th>الفحص</th><th>الرمز</th><th>النتيجة</th><th>الوحدة</th><th>المعدل الطبيعي</th><th>التقييم</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
<div class="footer">{report['disclaimer']}</div>
</body>
</html>"""

    safe_stem = Path(file_name).stem.replace(" ", "_")
    saved_path = REPORTS_DIR / f"CBC_Report_{safe_stem}_{stamp}.html"
    saved_path.write_text(html_content, encoding="utf-8")
    return html_content, saved_path
