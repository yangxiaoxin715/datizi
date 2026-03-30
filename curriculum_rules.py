GRADE_POLICIES = {
    "一年级": {
        "allowed": ["20以内加减", "看图数数", "简单比较", "凑十与拆分", "直观图示"],
        "forbidden": ["乘除法", "方程", "分数", "小数", "复杂数量关系"],
        "ceiling": "只允许使用一年级及以下已学内容，必须依赖直观图示、数数、拆分、简单加减。",
        "expression": "优先口头描述、数一数、画一画，绝不能直接上抽象符号。",
    },
    "二年级": {
        "allowed": ["表内乘除", "简单倍数关系", "长度时间人民币基础题", "两步以内数量关系"],
        "forbidden": ["方程", "分数应用题", "小数", "复杂比例关系"],
        "ceiling": "只允许使用二年级及以下已学内容，优先乘除意义、倍数关系和直观数量变化。",
        "expression": "优先用几组、几倍、几份来讲，尽量少用抽象字母。",
    },
    "三年级": {
        "allowed": ["万以内数", "乘除法竖式", "简单分数初步", "周长面积初步", "两三步数量关系"],
        "forbidden": ["方程", "小数运算", "比例", "复杂行程与工程"],
        "ceiling": "只允许使用三年级及以下已学内容，优先整数运算、简单分数直观理解和基础数量关系。",
        "expression": "可以进入两三步数量关系，但仍要优先直观图示和口头关系。",
    },
    "四年级": {
        "allowed": ["整数四则运算", "份数思维", "倍数关系", "对应关系", "数量关系分析"],
        "forbidden": ["方程", "用字母表示未知数", "分数方程", "比例法"],
        "ceiling": "只允许使用四年级及以下已学内容，优先份数、倍数、对应关系和数量关系，不得使用方程。",
        "expression": "先讲谁变了、谁没变，再讲份数、倍数和对应关系，不得一上来设x、y。",
    },
    "五年级": {
        "allowed": ["小数", "分数基础", "简易方程初步", "平均数", "较完整数量关系"],
        "forbidden": ["比例法", "超纲代数技巧", "复杂方程组"],
        "ceiling": "只允许使用五年级及以下已学内容，可以使用简易方程，但不能使用比例法和更高年级代数技巧。",
        "expression": "可以使用简易方程，但仍要先交代数量关系，再进入字母表示。",
    },
    "六年级": {
        "allowed": ["分数应用题", "比和比例初步", "百分数", "稍复杂方程", "较复杂数量关系"],
        "forbidden": ["初中代数", "二元一次方程组", "函数", "几何证明"],
        "ceiling": "只允许使用六年级及以下已学内容，可以使用分数、比例初步和稍复杂方程，但不能跨到初中方法。",
        "expression": "允许更完整的数量关系和稍复杂方程，但不能直接跨到初中符号套路。",
    },
}

TOPIC_BOUNDARIES = {
    "20以内加减": {"level": "一年级", "aliases": ["20以内加减", "凑十法", "破十法", "比大小", "看图列式"]},
    "100以内加减": {"level": "二年级", "aliases": ["100以内加减", "退位减法", "进位加法"]},
    "表内乘除": {"level": "二年级", "aliases": ["表内乘法", "表内除法", "乘除法意义", "倍数初步"]},
    "长度时间人民币": {"level": "二年级", "aliases": ["长度单位", "时间单位", "人民币"]},
    "万以内数": {"level": "三年级", "aliases": ["万以内数", "大数读写", "估算"]},
    "多位数乘除": {"level": "三年级", "aliases": ["乘除法竖式", "多位数乘一位数", "除法竖式"]},
    "分数初步": {"level": "三年级", "aliases": ["简单分数初步", "分数初步", "几分之一", "几分之几"]},
    "周长面积初步": {"level": "三年级", "aliases": ["周长", "面积初步", "长方形周长", "正方形周长"]},
    "整数四则": {"level": "四年级", "aliases": ["整数四则运算", "四则混合运算", "运算定律"]},
    "份数思维": {"level": "四年级", "aliases": ["份数思维", "倍数关系", "对应关系", "数量关系分析"]},
    "小数": {"level": "五年级", "aliases": ["小数意义", "小数加减", "小数乘除", "循环小数"]},
    "分数运算": {"level": "五年级", "aliases": ["分数基础", "分数加减", "分数乘法", "分数除法"]},
    "简易方程": {"level": "五年级", "aliases": ["简易方程", "用字母表示数", "列方程", "未知数"]},
    "平均数": {"level": "五年级", "aliases": ["平均数", "可能性", "统计图"]},
    "分数应用题": {"level": "六年级", "aliases": ["分数应用题", "单位1", "量率对应"]},
    "百分数": {"level": "六年级", "aliases": ["百分数", "折扣", "成数", "税率", "利率"]},
    "比和比例": {"level": "六年级", "aliases": ["比和比例", "比例", "正比例", "反比例", "按比例分配"]},
    "圆与几何": {"level": "六年级", "aliases": ["圆", "圆周率", "圆面积", "圆周长"]},
}

OUT_OF_SCOPE_HINTS = {
    "方程": ["用字母表示未知数", "根据等量关系列方程", "理解移项前后的数量关系不变"],
    "简易方程": ["用字母表示未知数", "根据等量关系列方程", "一步两步简易方程"],
    "比例": ["比的意义", "比和比例初步", "用比例描述数量关系"],
    "分数应用": ["分数的意义", "分数乘除基础", "用单位“1”分析数量关系"],
    "复杂数量关系": ["份数和倍数关系", "对应关系", "多步数量关系分析"],
}

TOPIC_PREREQUISITES = {
    "20以内加减": ["数数与数感", "10以内加减", "凑十与拆分"],
    "100以内加减": ["整十数加减", "进位加法", "退位减法"],
    "表内乘除": ["加法意义", "平均分", "乘法口诀"],
    "长度时间人民币": ["数数与单位感", "简单比较", "整十整百"],
    "万以内数": ["千以内数", "计数单位", "数位顺序"],
    "多位数乘除": ["表内乘除", "整十整百乘除", "竖式书写"],
    "分数初步": ["平均分", "图形直观分一分", "部分与整体"],
    "周长面积初步": ["长度单位", "长方形和正方形认识", "数格子"],
    "整数四则": ["多位数乘除", "运算顺序", "运算定律"],
    "份数思维": ["倍数关系", "对应关系", "整数四则"],
    "小数": ["十进制计数法", "分数与小数联系", "整数四则"],
    "分数运算": ["分数意义", "通分约分", "整数运算基础"],
    "简易方程": ["用字母表示未知数", "等量关系", "整数与小数分数基础运算"],
    "平均数": ["加减乘除", "总量与份数", "统计表"],
    "分数应用题": ["分数运算", "单位“1”", "量率对应"],
    "百分数": ["分数与小数互化", "比率意义", "乘除法"],
    "比和比例": ["比的意义", "分数应用题", "量之间的倍比关系"],
    "圆与几何": ["周长面积基础", "乘方感受", "π的直观理解"],
}


def grade_policy_text(level: str) -> str:
    policy = GRADE_POLICIES.get(level)
    if not policy:
        return "请严格按当前学习水平边界判断，不能偷用更高层级方法。"
    allowed = "、".join(policy["allowed"])
    forbidden = "、".join(policy["forbidden"])
    return (
        f"{policy['ceiling']} 允许方法：{allowed}。"
        f" 不得使用{forbidden}。"
        f" 表达要求：{policy['expression']}"
    )


def normalize_topic_name(text: str) -> str:
    if not text:
        return ""
    lowered = text.strip()
    for canonical, meta in TOPIC_BOUNDARIES.items():
        for alias in meta["aliases"]:
            if alias in lowered or lowered in alias:
                return canonical
    return ""


def topic_boundary_text(topic: str) -> str:
    canonical = normalize_topic_name(topic)
    if not canonical:
        return "未识别到明确知识点，按当前学习水平通用边界判断。"
    meta = TOPIC_BOUNDARIES[canonical]
    prereqs = "、".join(TOPIC_PREREQUISITES.get(canonical, []))
    return f"知识点“{canonical}”通常从{meta['level']}开始系统学习。前置知识：{prereqs}。"


def infer_missing_knowledge(reason: str, current_topic: str) -> list[str]:
    topic = normalize_topic_name(current_topic)
    if topic:
      return TOPIC_PREREQUISITES.get(topic, [])

    for keyword, hints in OUT_OF_SCOPE_HINTS.items():
        if keyword in reason:
            return hints

    for canonical, meta in TOPIC_BOUNDARIES.items():
        if canonical in reason or any(alias in reason for alias in meta["aliases"]):
            return TOPIC_PREREQUISITES.get(canonical, [])

    return []
