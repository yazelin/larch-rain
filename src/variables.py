"""全專案變數（design/重寫.md）。"""

VARS = {
    'phase': ('string', 'start', '進度：start／hub／climax'),
    'fade': ('number', 0, '逃避次數：方澄外套褪色程度'),
    'rooftop_done': ('boolean', False, '頂樓的鎖已打開'),
    'store_done': ('boolean', False, '超商的帳已結清'),
    'r17': ('string', '', '頂樓十七歲重播進度'),
    'store': ('string', '', '超商重播進度'),
}

RPG_VARS = [
    ('hp', 'rpgHp', 'number', 100),
    ('bag', 'inventory', 'string', '[]'),
    ('equipment', 'rpgEquipment', 'string', '{}'),
    ('state', 'rpgState', 'string', ''),
    ('used', 'inventoryLastUsed', 'string', ''),
    ('count', 'inventoryCount', 'number', 0)
]


def project_variables():
    return ([{'id': k, 'name': k, 'label': lab, 'type': t, 'defaultValue': d} for k, (t, d, lab) in VARS.items()]
            + [{'id': i, 'name': n, 'label': n, 'type': t, 'defaultValue': d} for i, n, t, d in RPG_VARS])
