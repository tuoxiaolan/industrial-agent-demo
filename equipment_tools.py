from database import save_ticket
PARAMETERS = {
    ("Device-A", "提升电机功率"): {
        "value": 3.0,
        "unit": "kW",
        "source": "Device-A-manual.md",
    },
    ("Device-A", "净负载（含料斗）"): {
        "value": 800,
        "unit": "kg",
        "source": "Device-A-manual.md",
    },
    ("Device-A", "设备重量"): {
        "value": 1200,
        "unit": "kg",
        "source": "Device-A-manual.md",
    },
    ("Device-A", "年度维护周期"): {
        "value": "每年或运行1500小时后，以先到者为准",
        "unit": "",
        "source": "Device-A-maintenance.md",
    },
    ("Device-B", "提升电机功率"): {
        "value": 4.0,
        "unit": "kW",
        "source": "Device-B-manual.md",
    },
    ("Device-B", "整粒电机功率"): {
        "value": 5.5,
        "unit": "kW",
        "source": "Device-B-manual.md",
    },
    ("Device-B", "整粒生产能力"): {
        "value": "100～1000",
        "unit": "kg/h",
        "source": "Device-B-manual.md",
    },
    ("Device-B", "净负载（含料斗）"): {
        "value": 1100,
        "unit": "kg",
        "source": "Device-B-manual.md",
    },
    ("Device-B", "设备重量"): {
        "value": 1500,
        "unit": "kg",
        "source": "Device-B-manual.md",
    },
    ("Device-B", "年度维护周期"): {
        "value": "每年或运行1200小时后，以先到者为准",
        "unit": "",
        "source": "Device-B-maintenance.md",
    },
}


FIELD_ALIASES = {
    "产能": "整粒生产能力",
    "处理能力": "整粒生产能力",
    "加工能力": "整粒生产能力",
    "生产能力": "整粒生产能力",
    "每小时处理量": "整粒生产能力",
    "重量": "设备重量",
}
MODEL_ALIASES = {
    "DEVICE-A": "Device-A",
    "DEVICE-B": "Device-B",
}
def normalize_model(model):
    value = model.strip().upper()
    return MODEL_ALIASES.get(value, value)




def create_maintenance_ticket(model, issue, evidence):
    if not model.strip() or not issue.strip():
        return {
            "ok": False,
            "error": "设备型号和问题描述不能为空",
        }

    ticket = save_ticket(
        model=normalize_model(model),
        issue=issue.strip(),
        evidence=evidence.strip(),
    )

    return {
        "ok": True,
        "ticket": ticket,
    }


def get_equipment_parameter(model, field):
    normalized_model = normalize_model(model)
    normalized_field = FIELD_ALIASES.get(field.strip(), field.strip())
    data = PARAMETERS.get((normalized_model, normalized_field))

    if data is None:
        return {
            "ok": False,
            "model": normalized_model,
            "field": normalized_field,
            "error": "未找到该型号和参数",
        }

    return {
        "ok": True,
        "model": normalized_model,
        "field": normalized_field,
        "value": data["value"],
        "unit": data["unit"],
        "source": data["source"],
    }