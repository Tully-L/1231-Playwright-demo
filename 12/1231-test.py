from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests
import logging

# ===================== 替代 app.common.enums.PhaseType =====================
# 自定义 PhaseType 枚举类，模拟原项目中的逻辑
class PhaseType:
    @staticmethod
    def get_phase_num(stage_key):
        """根据阶段key返回对应的阶段数字"""
        phase_map = {
            "discovery": 1,      # 发现阶段 → 1期
            "indenabling": 2,    # 赋能阶段 → 2期
            "clinical": 3        # 临床阶段 → 3期
        }
        return phase_map.get(stage_key, 1)  # 默认返回1期

# ===================== 替代 app.core.logger =====================
# 配置基础日志，模拟原项目的logger
logging.basicConfig(
    level=logging.DEBUG,  # 日志级别
    format="%(asctime)s - %(levelname)s - %(message)s"  # 日志格式
)
logger = logging.getLogger(__name__)

# ===================== 核心业务逻辑（无修改） =====================
# 阶段映射：根据页面进度条 class 后缀 → PhaseType.key
STAGE_MAP = {
    "one": "discovery",
    "two": "indenabling",
    "two_half": "clinical",
    "three": "clinical",
}

def fetch_data(url) -> list[dict]:
    headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        )
    }
    res = ""  # 初始化res，避免循环内赋值失败导致未定义
    for attempt in range(1, 4):
        try:
            resp = cffi_requests.get(url, impersonate='chrome110', timeout=10, headers=headers, verify=False)
            resp.raise_for_status()
            res = resp.text
            break
        except Exception as e:
            logger.debug(
                f"WAVELIFE pipeline 第 {attempt} 次抓取失败，异常为：{e}")
            if attempt == 3:
                logger.error(f"WAVELIFE pipeline 数据获取失败，异常为：{e}")
                return []  # 3次失败后直接返回空列表
    
    soup = BeautifulSoup(res, "lxml")

    monitor_date = datetime.now().strftime("%Y-%m-%d")
    rows = []
    current_product = ""
    # 每个 program 块
    for row_div in soup.select("section .pipeline-block .rows"):
        # 产品名 & 子标题
        name_tag = row_div.select_one(".rows-title h4")
        sub_tag = row_div.select_one(".rows-title .sub-title")
        if name_tag:                                     # ←2. 有<h4>就更新
            current_product = name_tag.get_text(strip=True)
        product_name = current_product
        indication = (sub_tag.get_text(strip=True) if sub_tag else "") or ""

        # 阶段
        stage_div = row_div.select_one(".status .rounded-block-stat")
        stage_key = "discovery"   # 默认
        if stage_div:
            # class 形如 "rounded-block-stat title bm-gradient-darkblue-cyan two_half"
            for cls in stage_div.get("class", []):
                if cls in STAGE_MAP:
                    stage_key = STAGE_MAP[cls]
                    break
        phase_num = PhaseType.get_phase_num(stage_key)

        # 权利 & 患者群体，仅作 comments 拼接
        rights = row_div.select_one(".rights p")
        population = row_div.select_one(".population p")
        comments_parts = []
        if rights:
            comments_parts.append(rights.get_text(strip=True))
        if population:
            comments_parts.append(f"Population: {population.get_text(strip=True)}")
        comments = " | ".join(comments_parts)

        row = {
                "company": "Wave Life Sciences",
                "company_zh": "波浪生命科学",
                "monitor_date": monitor_date,
                "product_name": product_name,
                "phase_number": phase_num,
                "category": None,
                "indication": indication,
                "description": None,
                "target_list": None,
                "comments": comments or f"PHASE {phase_num}",
                "source": "web",
                "source_url": url,
                "update_date": None,
                "original_phase_desc": stage_key,
                "snapshot_path": None,
            }
        rows.append(row)
        logger.debug("row: " + str(row))
    
    if not rows:
        msg = f"WAVELIFE pipeline 数据获取失败，异常为：未解析到任何有效记录"
        logger.error(msg)
    return rows

if __name__ == "__main__":
    # 运行测试
    data = fetch_data("https://wavelifesciences.com/pipeline/research-and-development/")
    # 打印结果
    print("\n===== 解析结果 =====")
    for idx, d in enumerate(data, 1):
        print(f"\n【第{idx}条】")
        for key, value in d.items():
            print(f"{key}: {value}")