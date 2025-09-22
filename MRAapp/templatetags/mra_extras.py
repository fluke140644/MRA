from django import template
import re

register = template.Library()

THAI_MONTHS = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม",
    8: "สิงหาคม", 9: "กันยายน", 10: "ตุลาคม",
    11: "พฤศจิกายน", 12: "ธันวาคม",
}

@register.filter
def format_audit_period(value, buddhist=False):
    """
    แปลง 'YYYY-MM' หรือ date/datetime -> 'เดือน ภาษาไทย ปี'
    ใส่พารามิเตอร์ 'th' หรือ True เพื่อใช้ปี พ.ศ. (+543)
    ตัวอย่าง: '2025-09' -> 'กันยายน 2025' หรือ 'กันยายน 2568'
    """
    if not value:
        return ""
    try:
        if hasattr(value, "year") and hasattr(value, "month"):
            year, month = int(value.year), int(value.month)
        else:
            s = str(value)
            parts = s.split("-")
            if len(parts) < 2:
                return value
            year, month = int(parts[0]), int(parts[1])

        name = THAI_MONTHS.get(month, "")
        if isinstance(buddhist, str):
            use_th = buddhist.lower() in ("1", "true", "yes", "y", "th", "thai", "buddhist")
        else:
            use_th = bool(buddhist)
        if use_th:
            year += 543
        return f"{name} {year}".strip()
    except Exception:
        return value


@register.filter
def thai_date(value, buddhist='th'):
    """
    แปลง date/datetime หรือสตริง 'YYYY-MM-DD'/'DD-MM-YYYY' -> 'D เดือนไทย YYYY/พ.ศ.'
    ใช้ปี พ.ศ. เมื่อ buddhist เป็น 'th', 'true', 1, ฯลฯ
    ใช้ปี ค.ศ. เมื่อ buddhist เป็นค่าว่าง/False
    """
    if not value:
        return ""

    y = m = d = None
    try:
        # date/datetime
        if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
            y, m, d = int(value.year), int(value.month), int(value.day)
        else:
            s = str(value).strip()
            parts = re.split(r"[-/]", s)
            if len(parts) >= 3:
                if len(parts[0]) == 4:
                    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                else:
                    d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
    except Exception:
        return value

    if not all([y, m, d]):
        return value

    # ปี พ.ศ. ?
    if isinstance(buddhist, str):
        use_th = buddhist.lower() in ("1", "true", "yes", "y", "th", "thai", "buddhist")
    else:
        use_th = bool(buddhist)
    if y >= 2400:
        pass
    elif use_th:
        y += 543

    month_name = THAI_MONTHS.get(m, "")
    return f"{d} {month_name} {y}".strip()



@register.filter(name="get_item")
def get_item(d, key):
    """
    ใช้ในเทมเพลตเพื่อดึง dict[key] โดยบังคับ key เป็น str
    เช่น sec.items_by_visit|get_item:'1'
    """
    try:
        if isinstance(d, dict):
            return d.get(str(key))
    except Exception:
        pass
    return None