TRACK_LABELS = {
    "sync": "同步课内",
    "advanced": "同年级拔高",
}


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

ADVANCED_GRADE_POLICIES = {
    "一年级": {
        "allowed": ["20以内加减", "比较推理", "简单和差关系", "从条件反推", "画图枚举"],
        "forbidden": ["乘除法", "方程", "分数", "小数", "复杂方程型应用题"],
        "ceiling": "允许一年级在不引入乘除法和方程的前提下，做简单拔高的比较、和差、反推题。",
        "expression": "依然必须用口头关系、画图和试一试，不能直接上抽象字母。",
    },
    "二年级": {
        "allowed": ["表内乘除", "差量变化", "简单和差关系", "简单周期规律", "较灵活数量比较"],
        "forbidden": ["方程", "分数应用", "小数", "比例", "多层嵌套数量关系"],
        "ceiling": "允许二年级在表内乘除和加减基础上做差量变化、和差和简单规律类拔高。",
        "expression": "先讲变化前后谁多谁少，再讲差距怎么变，不能偷用方程。",
    },
    "三年级": {
        "allowed": ["和差问题", "归一归总基础", "多步数量关系", "简单分数直观题", "列表或线段图"],
        "forbidden": ["方程", "比例", "复杂工程行程", "分数方程"],
        "ceiling": "允许三年级做和差、简单归总和多步数量关系拔高，但仍不能用方程。",
        "expression": "优先线段图、列表和关系句，不得直接列方程。",
    },
    "四年级": {
        "allowed": ["归总问题", "差倍问题", "较复杂对应关系", "基础工程思维", "多步数量关系"],
        "forbidden": ["方程", "比例法", "分数方程", "初中代数化套路"],
        "ceiling": "允许四年级做归总、差倍、基础工程思维等拔高题，但不能用方程和比例法。",
        "expression": "先抓关系图和对应关系，再做四则运算拆解。",
    },
    "五年级": {
        "allowed": ["简易方程", "较复杂工程问题", "分段变化", "相对速度基础", "分数与百分数综合"],
        "forbidden": ["二元一次方程组", "比例极值技巧", "初中函数"],
        "ceiling": "允许五年级做简易方程、分段变化和相对速度基础拔高，但不能跨到初中方法。",
        "expression": "可以用简易方程和分段分析，但仍要先讲清每一段发生了什么。",
    },
    "六年级": {
        "allowed": ["分数应用综合", "比和比例拔高", "分段行程", "较复杂相对速度", "稍复杂方程综合"],
        "forbidden": ["二元一次方程组", "函数", "几何证明", "初中竞赛技巧"],
        "ceiling": "允许六年级做课内拔高和常见奥数启蒙题，但不能跨到初中正式代数体系。",
        "expression": "允许更长链条分析，但仍需保持小学阶段可转述的思路。",
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

ADVANCED_TOPIC_BOUNDARIES = {
    "比较推理": {"level": "一年级", "aliases": ["谁多谁少", "比较推理", "多几少几", "哪一盘最多", "橘子最多"]},
    "差量变化": {"level": "二年级", "aliases": ["差量变化", "多多少", "又进来", "差距变化"]},
    "和差问题": {"level": "三年级", "aliases": ["和差问题", "年龄和", "和是", "比大", "比小"]},
    "归总问题": {"level": "四年级", "aliases": ["归总问题", "提前完成", "平均每天", "原计划每天"]},
    "分段相对速度": {"level": "五年级", "aliases": ["相向奔跑", "掉头", "相对速度", "分段行程", "相遇"]},
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
    return track_policy_text("sync", level)


def track_policy_text(track: str, level: str) -> str:
    policy_map = ADVANCED_GRADE_POLICIES if track == "advanced" else GRADE_POLICIES
    policy = policy_map.get(level)
    if not policy:
        label = TRACK_LABELS.get(track, "当前路线")
        return f"请严格按{label}的当前学习水平边界判断，不能偷用更高层级方法。"
    allowed = "、".join(policy["allowed"])
    forbidden = "、".join(policy["forbidden"])
    return (
        f"{policy['ceiling']} 允许方法：{allowed}。"
        f" 不得使用{forbidden}。"
        f" 表达要求：{policy['expression']}"
    )


def normalize_topic_name(text: str, track: str = "sync") -> str:
    if not text:
        return ""
    lowered = text.strip()
    topic_map = ADVANCED_TOPIC_BOUNDARIES if track == "advanced" else TOPIC_BOUNDARIES
    for canonical, meta in topic_map.items():
        for alias in meta["aliases"]:
            if alias in lowered or lowered in alias:
                return canonical
    return ""


def topic_boundary_text(topic: str, track: str = "sync") -> str:
    canonical = normalize_topic_name(topic, track)
    if not canonical:
        label = TRACK_LABELS.get(track, "当前路线")
        return f"未识别到明确知识点，按{label}的当前学习水平通用边界判断。"
    topic_map = ADVANCED_TOPIC_BOUNDARIES if track == "advanced" else TOPIC_BOUNDARIES
    meta = topic_map[canonical]
    prereqs = "、".join(TOPIC_PREREQUISITES.get(canonical, []))
    return f"知识点“{canonical}”通常从{meta['level']}开始系统学习。前置知识：{prereqs}。"


def infer_missing_knowledge(reason: str, current_topic: str, track: str = "sync") -> list[str]:
    topic = normalize_topic_name(current_topic, track)
    if topic:
        return TOPIC_PREREQUISITES.get(topic, [])

    for keyword, hints in OUT_OF_SCOPE_HINTS.items():
        if keyword in reason:
            return hints

    topic_map = ADVANCED_TOPIC_BOUNDARIES if track == "advanced" else TOPIC_BOUNDARIES
    for canonical, meta in topic_map.items():
        if canonical in reason or any(alias in reason for alias in meta["aliases"]):
            return TOPIC_PREREQUISITES.get(canonical, [])

    return []
