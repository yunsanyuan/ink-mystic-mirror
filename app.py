# app.py - 最终版（合婚评语优化，去除“几等”说法）
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import random
from lunar_python import Lunar, Solar

app = Flask(__name__)

# ==================== 辅助函数 ====================
SHI_CHEN_MAP = [
    (23, 1, "子"), (1, 3, "丑"), (3, 5, "寅"), (5, 7, "卯"),
    (7, 9, "辰"), (9, 11, "巳"), (11, 13, "午"), (13, 15, "未"),
    (15, 17, "申"), (17, 19, "酉"), (19, 21, "戌"), (21, 23, "亥")
]

def get_di_zhi_by_hour(hour):
    for start, end, dz in SHI_CHEN_MAP:
        if start <= hour < end:
            return dz
    return "子"

# 十神映射表
SHI_SHEN_MAP = {
    ('甲','甲'):'比肩', ('甲','乙'):'劫财', ('甲','丙'):'食神', ('甲','丁'):'伤官', ('甲','戊'):'偏财',
    ('甲','己'):'正财', ('甲','庚'):'七杀', ('甲','辛'):'正官', ('甲','壬'):'偏印', ('甲','癸'):'正印',
    ('乙','甲'):'劫财', ('乙','乙'):'比肩', ('乙','丙'):'伤官', ('乙','丁'):'食神', ('乙','戊'):'正财',
    ('乙','己'):'偏财', ('乙','庚'):'正官', ('乙','辛'):'七杀', ('乙','壬'):'正印', ('乙','癸'):'偏印',
    ('丙','甲'):'偏印', ('丙','乙'):'正印', ('丙','丙'):'比肩', ('丙','丁'):'劫财', ('丙','戊'):'食神',
    ('丙','己'):'伤官', ('丙','庚'):'偏财', ('丙','辛'):'正财', ('丙','壬'):'七杀', ('丙','癸'):'正官',
    ('丁','甲'):'正印', ('丁','乙'):'偏印', ('丁','丙'):'劫财', ('丁','丁'):'比肩', ('丁','戊'):'伤官',
    ('丁','己'):'食神', ('丁','庚'):'正财', ('丁','辛'):'偏财', ('丁','壬'):'正官', ('丁','癸'):'七杀',
    ('戊','甲'):'七杀', ('戊','乙'):'正官', ('戊','丙'):'偏印', ('戊','丁'):'正印', ('戊','戊'):'比肩',
    ('戊','己'):'劫财', ('戊','庚'):'食神', ('戊','辛'):'伤官', ('戊','壬'):'偏财', ('戊','癸'):'正财',
    ('己','甲'):'正官', ('己','乙'):'七杀', ('己','丙'):'正印', ('己','丁'):'偏印', ('己','戊'):'劫财',
    ('己','己'):'比肩', ('己','庚'):'伤官', ('己','辛'):'食神', ('己','壬'):'正财', ('己','癸'):'偏财',
    ('庚','甲'):'偏财', ('庚','乙'):'正财', ('庚','丙'):'七杀', ('庚','丁'):'正官', ('庚','戊'):'偏印',
    ('庚','己'):'正印', ('庚','庚'):'比肩', ('庚','辛'):'劫财', ('庚','壬'):'食神', ('庚','癸'):'伤官',
    ('辛','甲'):'正财', ('辛','乙'):'偏财', ('辛','丙'):'正官', ('辛','丁'):'七杀', ('辛','戊'):'正印',
    ('辛','己'):'偏印', ('辛','庚'):'劫财', ('辛','辛'):'比肩', ('辛','壬'):'伤官', ('辛','癸'):'食神',
    ('壬','甲'):'食神', ('壬','乙'):'伤官', ('壬','丙'):'偏财', ('壬','丁'):'正财', ('壬','戊'):'七杀',
    ('壬','己'):'正官', ('壬','庚'):'偏印', ('壬','辛'):'正印', ('壬','壬'):'比肩', ('壬','癸'):'劫财',
    ('癸','甲'):'伤官', ('癸','乙'):'食神', ('癸','丙'):'正财', ('癸','丁'):'偏财', ('癸','戊'):'正官',
    ('癸','己'):'七杀', ('癸','庚'):'正印', ('癸','辛'):'偏印', ('癸','壬'):'劫财', ('癸','癸'):'比肩',
}
def get_shi_shen(day_gan, other_gan):
    return SHI_SHEN_MAP.get((day_gan, other_gan), '未知')

# 地支五行映射
ZHI_WU_XING = {
    '寅':'木', '卯':'木', '巳':'火', '午':'火',
    '辰':'土', '戌':'土', '丑':'土', '未':'土',
    '申':'金', '酉':'金', '亥':'水', '子':'水'
}

# 藏干映射表
ZANG_GAN_MAP = {
    "子": "癸", "丑": "己癸辛", "寅": "甲丙戊", "卯": "乙",
    "辰": "戊乙癸", "巳": "丙戊庚", "午": "丁己", "未": "己丁乙",
    "申": "戊庚壬", "酉": "辛", "戌": "戊辛丁", "亥": "壬甲"
}
def get_hide_gan(zhi: str) -> str:
    return ZANG_GAN_MAP.get(zhi, "")

# ==================== 称骨算命模块 ====================
NIAN_WEIGHT = {
    "甲子": 1.2, "乙丑": 1.0, "丙寅": 0.6, "丁卯": 0.8, "戊辰": 1.2, "己巳": 0.5,
    "庚午": 0.9, "辛未": 0.8, "壬申": 0.7, "癸酉": 1.2, "甲戌": 1.5, "乙亥": 0.9,
    "丙子": 1.6, "丁丑": 0.8, "戊寅": 0.8, "己卯": 1.9, "庚辰": 1.2, "辛巳": 0.6,
    "壬午": 0.8, "癸未": 0.7, "甲申": 0.5, "乙酉": 1.5, "丙戌": 0.6, "丁亥": 1.6,
    "戊子": 1.5, "己丑": 0.7, "庚寅": 0.9, "辛卯": 1.2, "壬辰": 1.0, "癸巳": 0.7,
    "甲午": 1.5, "乙未": 0.6, "丙申": 0.5, "丁酉": 1.4, "戊戌": 1.4, "己亥": 0.9,
    "庚子": 0.7, "辛丑": 0.7, "壬寅": 0.9, "癸卯": 1.2, "甲辰": 0.8, "乙巳": 0.7,
    "丙午": 1.3, "丁未": 0.5, "戊申": 1.4, "己酉": 0.5, "庚戌": 0.9, "辛亥": 1.7,
    "壬子": 0.5, "癸丑": 0.7, "甲寅": 1.2, "乙卯": 0.8, "丙辰": 0.8, "丁巳": 0.6,
    "戊午": 1.9, "己未": 0.6, "庚申": 0.8, "辛酉": 1.6, "壬戌": 1.0, "癸亥": 0.7
}
YUE_WEIGHT = {1:0.6,2:0.7,3:1.8,4:0.9,5:0.5,6:1.6,7:0.9,8:1.5,9:1.8,10:0.8,11:0.9,12:0.5}
RI_WEIGHT = {
    1:0.5,2:1.0,3:0.8,4:1.5,5:1.6,6:1.5,7:0.8,8:1.6,9:0.8,10:1.6,
    11:0.9,12:1.7,13:0.8,14:1.7,15:1.0,16:0.8,17:0.9,18:1.8,19:0.5,20:1.5,
    21:1.0,22:0.9,23:0.8,24:0.9,25:1.5,26:1.8,27:0.7,28:0.8,29:1.6,30:0.6
}
SHI_WEIGHT = {
    "子":1.6,"丑":0.6,"寅":0.7,"卯":1.0,"辰":0.9,"巳":1.6,
    "午":1.0,"未":0.8,"申":0.8,"酉":0.9,"戌":0.6,"亥":0.6
}
CHENG_GU_POEM = {
    (2.1,2.5): "此命推来骨格轻，求谋作事事难成。妻儿兄弟应难许，别处他乡作散人。",
    (2.6,3.0): "此命推来骨肉轻，求财谋事难成功。若遇贵人相扶助，犹如枯木逢春荣。",
    (3.1,3.5): "此命生来福不轻，事事求谋皆称心。东西南北皆通达，终身富贵享荣华。",
    (3.6,4.0): "此命生来福禄全，家业兴隆万事安。中年自有贵人助，晚年逍遥乐自然。",
    (4.1,4.5): "此命生来福泽深，财禄丰盈万事兴。一生近贵多成就，晚景荣华胜子孙。",
    (4.6,5.0): "此命生来福气高，财源滚滚胜波涛。中年得意功名就，晚景荣华福寿牢。",
    (5.1,5.5): "此命生来福禄全，荣华富贵万万年。金银财宝堆满库，子孙兴旺福连绵。",
    (5.6,6.0): "此命生来福寿长，荣华富贵不寻常。一生享受皇家禄，晚景逍遥胜帝王。",
    (6.1,6.5): "此命生来福气强，功名富贵两相当。一生近贵多荣耀，百岁高龄寿且康。",
    (6.6,7.2): "此命生来福禄崇，荣华富贵享无穷。一生心善多行德，位列三台福寿隆。"
}
def get_cheng_gu_comment(total_weight):
    for (low, high), poem in CHENG_GU_POEM.items():
        if low <= total_weight <= high:
            return poem
    return "此命非凡，福祸相依。须当积德行善，自有天相。"

# ==================== 周易六爻模块 ====================
BA_GUA = {
    "111": "乾", "110": "兑", "101": "离", "100": "震",
    "011": "巽", "010": "坎", "001": "艮", "000": "坤"
}
LIU_SHI_SI_GUA = {
    ("乾","乾"): ("乾为天","元亨利贞。"), ("坤","坤"): ("坤为地","元亨，利牝马之贞。"),
    ("震","震"): ("震为雷","亨。震来虩虩，笑言哑哑。"), ("巽","巽"): ("巽为风","小亨，利有攸往，利见大人。"),
    ("坎","坎"): ("坎为水","习坎，有孚，维心亨，行有尚。"), ("离","离"): ("离为火","利贞，亨。畜牝牛，吉。"),
    ("艮","艮"): ("艮为山","艮其背，不获其身，行其庭，不见其人。"), ("兑","兑"): ("兑为泽","亨，利贞。"),
    ("乾","坤"): ("天地否","否之匪人，不利君子贞，大往小来。"), ("坤","乾"): ("地天泰","小往大来，吉亨。"),
    ("乾","震"): ("天雷无妄","元亨，利贞。其匪正有眚，不利有攸往。"), ("震","乾"): ("雷天大壮","利贞。"),
    ("乾","坎"): ("天水讼","有孚窒惕，中吉，终凶。利见大人，不利涉大川。"), ("坎","乾"): ("水天需","有孚，光亨，贞吉。利涉大川。"),
    ("乾","艮"): ("天山遁","亨，小利贞。"), ("艮","乾"): ("山天大畜","利贞，不家食吉，利涉大川。"),
    ("坤","震"): ("地雷复","亨。出入无疾，朋来无咎。"), ("震","坤"): ("雷地豫","利建侯行师。"),
    ("坤","坎"): ("地水师","贞，丈人吉，无咎。"), ("坎","坤"): ("水地比","吉。原筮，元永贞，无咎。"),
    ("坤","艮"): ("地山谦","亨，君子有终。"), ("艮","坤"): ("山地剥","不利有攸往。"),
    ("震","坎"): ("雷水解","利西南，无所往，其来复吉。"), ("坎","震"): ("水雷屯","元亨利贞。勿用有攸往，利建侯。"),
    ("震","艮"): ("雷山小过","亨，利贞。可小事，不可大事。"), ("艮","震"): ("山雷颐","贞吉。观颐，自求口实。"),
    ("坎","艮"): ("水山蹇","利西南，不利东北。利见大人，贞吉。"), ("艮","坎"): ("山水蒙","亨。匪我求童蒙，童蒙求我。"),
    ("离","乾"): ("火天大有","元亨。"), ("乾","离"): ("天火同人","于野，亨。利涉大川，利君子贞。"),
    ("离","坤"): ("火地晋","康侯用锡马蕃庶，昼日三接。"), ("坤","离"): ("地火明夷","利艰贞。"),
    ("离","震"): ("火雷噬嗑","亨，利用狱。"), ("震","离"): ("雷火丰","亨，王假之，勿忧，宜日中。"),
    ("离","坎"): ("火水未济","亨。小狐汔济，濡其尾，无攸利。"), ("坎","离"): ("水火既济","亨小，利贞。初吉终乱。"),
    ("离","艮"): ("火山旅","小亨，旅贞吉。"), ("艮","离"): ("山火贲","亨。小利有攸往。"),
    ("兑","乾"): ("泽天夬","扬于王庭，孚号有厉。"), ("乾","兑"): ("天泽履","履虎尾，不咥人，亨。"),
    ("兑","坤"): ("泽地萃","亨。王假有庙。"), ("坤","兑"): ("地泽临","元亨利贞。至于八月有凶。"),
    ("兑","震"): ("泽雷随","元亨利贞，无咎。"), ("震","兑"): ("雷泽归妹","征凶，无攸利。"),
    ("兑","坎"): ("泽水困","亨，贞，大人吉，无咎。"), ("坎","兑"): ("水泽节","亨。苦节不可贞。"),
    ("兑","艮"): ("泽山咸","亨，利贞，取女吉。"), ("艮","兑"): ("山泽损","有孚，元吉，无咎，可贞，利有攸往。"),
    ("巽","乾"): ("风天小畜","亨。密云不雨，自我西郊。"), ("乾","巽"): ("天风姤","女壮，勿用取女。"),
    ("巽","坤"): ("风地观","盥而不荐，有孚颙若。"), ("坤","巽"): ("地风升","元亨，用见大人，勿恤，南征吉。"),
    ("巽","震"): ("风雷益","利有攸往，利涉大川。"), ("震","巽"): ("雷风恒","亨，无咎，利贞，利有攸往。"),
    ("巽","坎"): ("风水涣","亨。王假有庙，利涉大川。"), ("坎","巽"): ("水风井","改邑不改井，无丧无得，往来井井。"),
    ("巽","艮"): ("风山渐","女归吉，利贞。"), ("艮","巽"): ("山风蛊","元亨，利涉大川。先甲三日，后甲三日。"),
    ("巽","离"): ("风火家人","利女贞。"), ("离","巽"): ("火风鼎","元吉，亨。"),
    ("兑","巽"): ("泽风大过","栋桡，利有攸往，亨。"), ("巽","兑"): ("风泽中孚","豚鱼吉，利涉大川，利贞。"),
    ("离","兑"): ("火泽睽","小事吉。"), ("兑","离"): ("泽火革","己日乃孚，元亨利贞，悔亡。"),
}
def get_hexagram_name_and_text(shang_gua, xia_gua):
    return LIU_SHI_SI_GUA.get((shang_gua, xia_gua), ("未知卦", "此卦象深邃，难以言表。"))

def yaogua_random():
    results = []
    for _ in range(6):
        coins = [random.randint(0, 1) for _ in range(3)]
        yang_count = sum(coins)
        if yang_count == 3:
            yin_yang, is_bian = 1, True
        elif yang_count == 0:
            yin_yang, is_bian = 0, True
        elif yang_count == 2:
            yin_yang, is_bian = 0, False
        else:
            yin_yang, is_bian = 1, False
        results.append({"yin_yang": yin_yang, "is_bian": is_bian})
    return results

def build_hexagram_from_yao(yao_list):
    xia_gua_bin = "".join(str(yao["yin_yang"]) for yao in yao_list[:3][::-1])
    shang_gua_bin = "".join(str(yao["yin_yang"]) for yao in yao_list[3:][::-1])
    ben_gua = (BA_GUA.get(shang_gua_bin, "?"), BA_GUA.get(xia_gua_bin, "?"))
    bian_yao_list = []
    for yao in yao_list:
        if yao["is_bian"]:
            bian_yao_list.append({"yin_yang": 1 - yao["yin_yang"], "is_bian": False})
        else:
            bian_yao_list.append({"yin_yang": yao["yin_yang"], "is_bian": False})
    xia_gua_bin_b = "".join(str(yao["yin_yang"]) for yao in bian_yao_list[:3][::-1])
    shang_gua_bin_b = "".join(str(yao["yin_yang"]) for yao in bian_yao_list[3:][::-1])
    bian_gua = (BA_GUA.get(shang_gua_bin_b, "?"), BA_GUA.get(xia_gua_bin_b, "?"))
    return ben_gua, bian_gua

# ==================== 八字合婚模块 ====================
SHENGXIAO_LIUHE = {
    "鼠": "牛", "牛": "鼠", "虎": "猪", "猪": "虎",
    "兔": "狗", "狗": "兔", "龙": "鸡", "鸡": "龙",
    "蛇": "猴", "猴": "蛇", "马": "羊", "羊": "马"
}
SHENGXIAO_SANHE = [
    ("鼠", "龙", "猴"), ("牛", "蛇", "鸡"), ("虎", "马", "狗"),
    ("兔", "羊", "猪"), ("龙", "鼠", "猴"), ("蛇", "牛", "鸡"),
    ("马", "虎", "狗"), ("羊", "兔", "猪"), ("猴", "鼠", "龙"),
    ("鸡", "牛", "蛇"), ("狗", "虎", "马"), ("猪", "兔", "羊")
]
SHENGXIAO_CHONG = {
    "鼠": "马", "马": "鼠", "牛": "羊", "羊": "牛",
    "虎": "猴", "猴": "虎", "兔": "鸡", "鸡": "兔",
    "龙": "狗", "狗": "龙", "蛇": "猪", "猪": "蛇"
}
SHENGXIAO_XING = {
    "鼠": "兔", "兔": "鼠",
    "虎": "蛇", "蛇": "虎", "蛇": "猴", "猴": "蛇", "虎": "猴", "猴": "虎",
    "牛": "狗", "狗": "牛", "牛": "羊", "羊": "牛", "狗": "羊", "羊": "狗",
    "龙": "龙", "马": "马", "鸡": "鸡", "猪": "猪"
}
TIANGAN_WUHE = {
    ("甲", "己"): "中正之合", ("己", "甲"): "中正之合",
    ("乙", "庚"): "仁义之合", ("庚", "乙"): "仁义之合",
    ("丙", "辛"): "威制之合", ("辛", "丙"): "威制之合",
    ("丁", "壬"): "淫慝之合", ("壬", "丁"): "淫慝之合",
    ("戊", "癸"): "无情之合", ("癸", "戊"): "无情之合",
}
DIZHI_LIUHE = {
    ("子", "丑"): "土", ("丑", "子"): "土",
    ("寅", "亥"): "木", ("亥", "寅"): "木",
    ("卯", "戌"): "火", ("戌", "卯"): "火",
    ("辰", "酉"): "金", ("酉", "辰"): "金",
    ("巳", "申"): "水", ("申", "巳"): "水",
    ("午", "未"): "土", ("未", "午"): "土",
}
WUXING_COMPLEMENT = {
    ("木", "火"): 10, ("火", "木"): 10,
    ("火", "土"): 10, ("土", "火"): 10,
    ("土", "金"): 10, ("金", "土"): 10,
    ("金", "水"): 10, ("水", "金"): 10,
    ("水", "木"): 10, ("木", "水"): 10,
    ("木", "木"): 5, ("火", "火"): 5, ("土", "土"): 5, ("金", "金"): 5, ("水", "水"): 5,
    ("木", "金"): -5, ("金", "木"): -5,
    ("火", "水"): -5, ("水", "火"): -5,
    ("土", "木"): -5, ("木", "土"): -5,
    ("土", "水"): -5, ("水", "土"): -5,
    ("火", "金"): -5, ("金", "火"): -5,
}

def get_shengxiao_from_ganzhi(year_ganzhi):
    zhi = year_ganzhi[1]
    zhi_sx = {"子":"鼠","丑":"牛","寅":"虎","卯":"兔","辰":"龙","巳":"蛇",
              "午":"马","未":"羊","申":"猴","酉":"鸡","戌":"狗","亥":"猪"}
    return zhi_sx.get(zhi, "未知")

def get_wuxing_from_gan(gan):
    wuxing = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
    return wuxing.get(gan, "土")

# ==================== Flask 路由 ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bazi', methods=['POST'])
def bazi_cal():
    try:
        data = request.json
        year = int(data['year'])
        month = int(data['month'])
        day = int(data['day'])
        hour = int(data['hour'])
        if not (1900 <= year <= 2100) or not (1 <= month <= 12) or not (1 <= day <= 31) or not (0 <= hour <= 23):
            return jsonify({"success": False, "message": "日期或时辰超出合理范围"}), 400
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        year_pillar = lunar.getYearInGanZhi()
        month_pillar = lunar.getMonthInGanZhi()
        day_pillar = lunar.getDayInGanZhi()
        time_pillar = lunar.getTimeInGanZhi()
        day_master = day_pillar[0]
        year_gan = year_pillar[0]
        month_gan = month_pillar[0]
        time_gan = time_pillar[0]
        ten_gods = {
            "年干": get_shi_shen(day_master, year_gan),
            "月干": get_shi_shen(day_master, month_gan),
            "日干": "日主",
            "时干": get_shi_shen(day_master, time_gan)
        }
        month_zhi = month_pillar[1]
        wu_xing = {w: "中和" for w in "木火土金水"}
        if month_zhi in ZHI_WU_XING:
            strong = ZHI_WU_XING[month_zhi]
            wu_xing[strong] = "旺"
            if strong == '木': wu_xing['土'] = '弱'
            elif strong == '火': wu_xing['金'] = '弱'
            elif strong == '土': wu_xing['水'] = '弱'
            elif strong == '金': wu_xing['木'] = '弱'
            elif strong == '水': wu_xing['火'] = '弱'
        zhi_list = [year_pillar[1], month_pillar[1], day_pillar[1], time_pillar[1]]
        cang_gan = {
            "年支": get_hide_gan(zhi_list[0]),
            "月支": get_hide_gan(zhi_list[1]),
            "日支": get_hide_gan(zhi_list[2]),
            "时支": get_hide_gan(zhi_list[3]),
        }
        return jsonify({
            "success": True,
            "year_pillar": year_pillar,
            "month_pillar": month_pillar,
            "day_pillar": day_pillar,
            "time_pillar": time_pillar,
            "day_master": day_master,
            "ten_gods": ten_gods,
            "wu_xing": wu_xing,
            "cang_gan": cang_gan
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/chenggu', methods=['POST'])
def chenggu():
    try:
        data = request.json
        year = int(data['year'])
        month = int(data['month'])
        day = int(data['day'])
        hour = int(data['hour'])
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        ganzhi_year = lunar.getYearInGanZhi()
        lunar_month = lunar.getMonth()
        lunar_day = lunar.getDay()
        di_zhi = get_di_zhi_by_hour(hour)
        year_weight = NIAN_WEIGHT.get(ganzhi_year, 0.0)
        month_weight = YUE_WEIGHT.get(lunar_month, 0.0)
        day_weight = RI_WEIGHT.get(lunar_day, 0.0)
        hour_weight = SHI_WEIGHT.get(di_zhi, 0.0)
        total_weight = year_weight + month_weight + day_weight + hour_weight
        comment = get_cheng_gu_comment(total_weight)
        liang = int(total_weight)
        qian = int(round((total_weight - liang) * 10, 0))
        return jsonify({
            "success": True,
            "total_weight": f"{liang}两{qian}钱",
            "weight_detail": {
                "year": f"{ganzhi_year} {year_weight}两",
                "month": f"{lunar_month}月 {month_weight}两",
                "day": f"{lunar_day}日 {day_weight}两",
                "hour": f"{di_zhi}时 {hour_weight}两"
            },
            "comment": comment
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/yaogua', methods=['POST'])
def yaogua():
    try:
        yao_results = yaogua_random()
        ben_gua, bian_gua = build_hexagram_from_yao(yao_results)
        ben_name, ben_text = get_hexagram_name_and_text(ben_gua[0], ben_gua[1])
        bian_name, bian_text = get_hexagram_name_and_text(bian_gua[0], bian_gua[1])
        yao_display = []
        for i, yao in enumerate(yao_results[::-1]):
            symbol = "⚊" if yao["yin_yang"] == 1 else "⚋"
            if yao["is_bian"]:
                symbol += " (变)"
            yao_display.append(f"第{6-i}爻: {symbol}")
        return jsonify({
            "success": True,
            "ben_gua": f"{ben_gua[0]}{ben_gua[1]}",
            "ben_name": ben_name,
            "ben_text": ben_text,
            "bian_gua": f"{bian_gua[0]}{bian_gua[1]}",
            "bian_name": bian_name,
            "bian_text": bian_text,
            "yao_lines": yao_display
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/huangli', methods=['GET'])
def huangli():
    try:
        today = Solar.fromDate(datetime.now())
        lunar = today.getLunar()
        lunar_date = f"{lunar.getYearInGanZhi()}年 {lunar.getMonth()}月 {lunar.getDay()}日"
        try:
            jie = lunar.getJie()
            qi = lunar.getQi()
            solar_term = f"{jie} {qi}".strip() if jie or qi else "无"
        except AttributeError:
            solar_term = "无"
        try:
            yi = lunar.getDayYi()
            if isinstance(yi, str):
                yi = [item.strip() for item in yi.split(',') if item.strip()]
            ji = lunar.getDayJi()
            if isinstance(ji, str):
                ji = [item.strip() for item in ji.split(',') if item.strip()]
        except AttributeError:
            yi = ["宜祭祀", "宜祈福"]
            ji = ["忌嫁娶", "忌动土"]
        try:
            chong_sha = lunar.getChong()
        except AttributeError:
            chong_sha = "无"
        try:
            shen_sha = lunar.getShenSha()
        except AttributeError:
            shen_sha = "无"
        return jsonify({
            "success": True,
            "lunar_date": lunar_date,
            "solar_term": solar_term,
            "yi": yi[:5] if len(yi) > 5 else yi,
            "ji": ji[:5] if len(ji) > 5 else ji,
            "chong_sha": chong_sha,
            "shen_sha": shen_sha
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== 八字合婚路由（优化评语，去除等级称呼） ====================
@app.route('/api/hehun', methods=['POST'])
def hehun():
    try:
        data = request.json
        m_year = int(data['man_year'])
        m_month = int(data['man_month'])
        m_day = int(data['man_day'])
        m_hour = int(data['man_hour'])
        f_year = int(data['woman_year'])
        f_month = int(data['woman_month'])
        f_day = int(data['woman_day'])
        f_hour = int(data['woman_hour'])
        
        man_solar = Solar.fromYmdHms(m_year, m_month, m_day, m_hour, 0, 0)
        man_lunar = man_solar.getLunar()
        man_year_pillar = man_lunar.getYearInGanZhi()
        man_month_pillar = man_lunar.getMonthInGanZhi()
        man_day_pillar = man_lunar.getDayInGanZhi()
        man_hour_pillar = man_lunar.getTimeInGanZhi()
        man_day_master = man_day_pillar[0]
        man_day_zhi = man_day_pillar[1]
        
        woman_solar = Solar.fromYmdHms(f_year, f_month, f_day, f_hour, 0, 0)
        woman_lunar = woman_solar.getLunar()
        woman_year_pillar = woman_lunar.getYearInGanZhi()
        woman_month_pillar = woman_lunar.getMonthInGanZhi()
        woman_day_pillar = woman_lunar.getDayInGanZhi()
        woman_hour_pillar = woman_lunar.getTimeInGanZhi()
        woman_day_master = woman_day_pillar[0]
        woman_day_zhi = woman_day_pillar[1]
        
        # 生肖合婚
        man_sx = get_shengxiao_from_ganzhi(man_year_pillar)
        woman_sx = get_shengxiao_from_ganzhi(woman_year_pillar)
        sx_score = 0
        sx_detail = ""
        if SHENGXIAO_LIUHE.get(man_sx) == woman_sx:
            sx_score = 25
            sx_detail = f"生肖{man_sx}{woman_sx}六合，大吉。"
        elif (man_sx, woman_sx) in [(a,b) for group in SHENGXIAO_SANHE for a,b in [(group[0],group[1]),(group[0],group[2]),(group[1],group[2])]]:
            sx_score = 15
            sx_detail = f"生肖{man_sx}{woman_sx}三合，吉。"
        elif SHENGXIAO_CHONG.get(man_sx) == woman_sx:
            sx_score = -10
            sx_detail = f"生肖{man_sx}{woman_sx}相冲，不利。"
        elif SHENGXIAO_XING.get(man_sx) == woman_sx or SHENGXIAO_XING.get(woman_sx) == man_sx:
            sx_score = -5
            sx_detail = f"生肖{man_sx}{woman_sx}相刑，有矛盾。"
        else:
            sx_score = 5
            sx_detail = f"生肖{man_sx}{woman_sx}无冲合，平。"
        
        # 年柱纳音简化为年干五行相生
        man_year_gan = man_year_pillar[0]
        woman_year_gan = woman_year_pillar[0]
        year_wuxing_score = 0
        if get_wuxing_from_gan(man_year_gan) == get_wuxing_from_gan(woman_year_gan):
            year_wuxing_score = 5
        elif (get_wuxing_from_gan(man_year_gan), get_wuxing_from_gan(woman_year_gan)) in [('木','火'),('火','土'),('土','金'),('金','水'),('水','木')]:
            year_wuxing_score = 10
        else:
            year_wuxing_score = 0
        
        # 日干五合
        gan_score = 0
        gan_detail = ""
        if (man_day_master, woman_day_master) in TIANGAN_WUHE:
            gan_score = 20
            gan_detail = f"日干{man_day_master}{woman_day_master}五合，情意相投。"
        else:
            gan_score = 0
            gan_detail = "日干无合，普通。"
        
        # 日支六合/三合/冲刑
        zhi_score = 0
        zhi_detail = ""
        if (man_day_zhi, woman_day_zhi) in DIZHI_LIUHE:
            zhi_score = 20
            zhi_detail = f"日支{man_day_zhi}{woman_day_zhi}六合，情缘深厚。"
        elif (man_day_zhi, woman_day_zhi) in [('寅','戌'),('戌','寅'),('亥','卯'),('卯','亥'),('巳','酉'),('酉','巳'),('午','戌'),('戌','午'),('申','子'),('子','申')]:
            zhi_score = 15
            zhi_detail = f"日支{man_day_zhi}{woman_day_zhi}三合，和睦。"
        elif SHENGXIAO_CHONG.get(man_day_zhi, '') == woman_day_zhi or SHENGXIAO_CHONG.get(woman_day_zhi, '') == man_day_zhi:
            zhi_score = -10
            zhi_detail = f"日支{man_day_zhi}{woman_day_zhi}相冲，易有冲突。"
        else:
            zhi_score = 5
            zhi_detail = f"日支无特殊合冲，普通。"
        
        # 五行互补
        man_wx = get_wuxing_from_gan(man_day_master)
        woman_wx = get_wuxing_from_gan(woman_day_master)
        wuxing_score = WUXING_COMPLEMENT.get((man_wx, woman_wx), 0)
        if wuxing_score > 0:
            wuxing_score += 5
        elif wuxing_score < 0:
            wuxing_score -= 5
        else:
            wuxing_score = 5
        wuxing_detail = f"日主{man_day_master}({man_wx}) vs {woman_day_master}({woman_wx})"
        if wuxing_score > 0:
            wuxing_detail += f"，相生互补（+{wuxing_score}）"
        elif wuxing_score < 0:
            wuxing_detail += f"，相克冲突（{wuxing_score}）"
        else:
            wuxing_detail += "，相同或中性"
        
        # 总分
        total = sx_score + year_wuxing_score + gan_score + zhi_score + wuxing_score
        total += 20  # 基础分
        if total > 100: total = 100
        if total < 0: total = 0
        
        # 优化评语（去除“几等”说法，更温和尊重）
        if total >= 85:
            comment = "天赐良缘，情投意合。双方命理极为相合，婚姻幸福美满，堪称佳偶天成。"
        elif total >= 70:
            comment = "优良缘分，相得益彰。虽有微小摩擦，但总体和谐，是令人羡慕的良缘。"
        elif total >= 55:
            comment = "良好缘分，尚可互补。需双方多加沟通，以和为贵，可趋吉避凶。"
        elif total >= 40:
            comment = "需用心经营，多有磨合。建议慎重考虑，或通过风水调节，加强情感纽带。"
        else:
            comment = "挑战较多，需加倍努力。若执意一起，建议寻求专业指导，且双方需付出更多包容。"
        
        return jsonify({
            "success": True,
            "man_bazi": f"{man_year_pillar} {man_month_pillar} {man_day_pillar} {man_hour_pillar}",
            "woman_bazi": f"{woman_year_pillar} {woman_month_pillar} {woman_day_pillar} {woman_hour_pillar}",
            "shengxiao": {"man": man_sx, "woman": woman_sx, "score": sx_score, "detail": sx_detail},
            "tiangan": {"score": gan_score, "detail": gan_detail},
            "dizhi": {"score": zhi_score, "detail": zhi_detail},
            "wuxing": {"score": wuxing_score, "detail": wuxing_detail},
            "total_score": total,
            "comment": comment
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)