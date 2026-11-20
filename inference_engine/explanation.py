def format_fired_rule_explanation(rule_result: dict) -> dict:
    """صياغة تفسير واضح لكل قاعدة طبية تم تفعيلها."""
    alert_labels = {
        "urgent": "🚨 تنبيه عاجل",
        "warning": "⚠️ تحذير طبي",
        "info": "ℹ️ ملاحظة تشخيصية",
    }
    alert_type = rule_result.get("alert", "info")

    return {
        "rule_id": rule_result.get("rule_id", "—"),
        "name": rule_result.get("name", ""),
        "alert_type": alert_type,
        "alert_label": alert_labels.get(alert_type, "ℹ️ ملاحظة تشخيصية"),
        "conclusion": rule_result.get("conclusion", ""),
        "explanation": rule_result.get("explanation", ""),
        "details": rule_result.get("details", {}),
    }


def build_explanation_report(inference_output: dict) -> dict:
    """وحدة التفسير (Explanation Facility) لتوضيح سبب التشخيص وتصنيف النتائج."""
    fired_rules = inference_output.get("fired_rules", [])
    statuses = inference_output.get("statuses", {})
    total_rules = inference_output.get("total_rules", 30)
    checked_count = inference_output.get("checked_count", 0)
    fired_count = inference_output.get("fired_count", 0)

    urgent_findings = []
    warning_findings = []
    info_findings = []

    for r in fired_rules:
        if r.get("rule_id") == "R23":
            continue

        formatted = format_fired_rule_explanation(r)
        if formatted["alert_type"] == "urgent":
            urgent_findings.append(formatted)
        elif formatted["alert_type"] == "warning":
            warning_findings.append(formatted)
        else:
            info_findings.append(formatted)

    if urgent_findings:
        overall_status = "urgent"
        overall_headline = "توجد مؤشرات تستدعي مراجعة طبية عاجلة"
    elif warning_findings:
        overall_status = "warning"
        overall_headline = "توجد ملاحظات وتنبيهات طبية تستوجب المتابعة"
    elif info_findings:
        overall_status = "info"
        overall_headline = "تم رصد بعض التغيرات في مؤشرات صورة الدم"
    else:
        overall_status = "normal"
        overall_headline = "جميع مؤشرات صورة الدم الكاملة (CBC) ضمن الحدود الطبيعية"

    abnormal_tests = [
        info for info in statuses.values()
        if info.get("status") in ("منخفض", "مرتفع")
    ]

    how_trace = (
        f"قام محرك الاستدلال بفحص ({checked_count}) قاعدة من أصل ({total_rules}) قاعدة "
        f"باستخدام الاستدلال الأمامي (Forward Chaining)، وتم تفعيل ({fired_count}) قاعدة منطبقة على بيانات التقرير."
    )

    return {
        "overall_status": overall_status,
        "overall_headline": overall_headline,
        "has_clinical_findings": bool(urgent_findings or warning_findings or info_findings),
        "urgent_findings": urgent_findings,
        "warning_findings": warning_findings,
        "info_findings": info_findings,
        "abnormal_tests": abnormal_tests,
        "how_trace": how_trace,
        "disclaimer": "تنبيه: هذا التحليل ناتج عن نظام خبير مساعد ولا يُعد بديلاً عن التشخيص الطبي المباشر من قبل الطبيب المختص.",
    }