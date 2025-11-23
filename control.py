import optuna
from playwright.sync_api import sync_playwright
import time
import re

# ==========================================
# [설정] 최적화 타겟 (범위 확장 버전)
# ==========================================
PARAMS = {
    # 1. 분석 길이 (Index 4)
    # 기존: 10~60 -> 변경 없음
    "len": {"index": 4, "min": 4, "max": 60, "step": 2},
    
    # 2. 손절 트리거 % (Index 42) -> [수정됨]
    # 기존: 0.1 ~ 3.0 (너무 좁음)
    # 변경: 1.0 ~ 30.0 (기본값 20을 포함하여 넓게 탐색)
    # 단위: 0.5 단위로 큼직하게 찾기
    "sl_trigger": {"index": 42, "min": 10.0, "max": 30.0, "step": 1},
    
    # 3. 익절 트리거 % (Index 43) -> [수정됨]
    # 기존: 0.5 ~ 10.0
    # 변경: 1.0 ~ 40.0 (손절이 20이면 익절은 그보다 커야 할 수도 있음)
    "tp_trigger": {"index": 43, "min": 0.05, "max": 2.0, "step": 0.05},
}

# DB 저장 설정 (이어하기 가능)
DB_URL = "sqlite:///trading_opt.db"
STUDY_NAME = "strategy_real_v2" # 이름 변경 (새 마음으로 시작)

CDP_URL = "http://localhost:9222"
# ==========================================

def get_performance(page):
    """하단 패널 데이터 읽기 (마이너스, 승률 완벽 대응)"""
    try:
        panel = page.locator(".bottom-widgetbar-content.backtesting")
        full_text = panel.inner_text()
        
        if not full_text.strip():
            time.sleep(1)
            full_text = panel.inner_text()

        # 순익 추출
        profit_match = re.search(r'(총 손익|Net Profit)[\s\n]+([+\-−]?[\d,]+\.?\d*)', full_text)
        # 승률 추출 (수익성 거래 뒤의 %)
        win_match = re.search(r'(수익성 거래|Percent Profitable)[\s\S]*?([\d\.]+)%', full_text)
        
        profit = 0.0
        win_rate = 0.0
        
        if profit_match:
            clean_val = profit_match.group(2).replace(',', '').replace('−', '-')
            profit = float(clean_val)
        
        if win_match:
            win_rate = float(win_match.group(2))
            
        return profit, win_rate

    except Exception:
        return -999999, 0

def objective(trial):
    """AI 실험 수행"""
    
    # 1. 값 제안 (AI가 이번에 시도할 값)
    p_len = trial.suggest_int('len', PARAMS["len"]["min"], PARAMS["len"]["max"], step=PARAMS["len"]["step"])
    p_sl  = trial.suggest_float('sl_trigger', PARAMS["sl_trigger"]["min"], PARAMS["sl_trigger"]["max"], step=PARAMS["sl_trigger"]["step"])
    p_tp  = trial.suggest_float('tp_trigger', PARAMS["tp_trigger"]["min"], PARAMS["tp_trigger"]["max"], step=PARAMS["tp_trigger"]["step"])

    print(f"\n🔄 [Trial {trial.number}] 길이:{p_len} | 손절:{p_sl:.1f}% | 익절:{p_tp:.1f}%")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            context = browser.contexts[0]
            page = None
            for p_tab in context.pages:
                if "TradingView" in p_tab.title() or "BTC" in p_tab.title():
                    page = p_tab
                    break
            if not page: page = context.pages[0]

            dialog = page.locator("div[data-name='indicator-properties-dialog']")
            if not dialog.is_visible():
                print("❌ 설정창이 닫혔습니다.")
                return -999999

            inputs = dialog.locator("input").all()
            
            # 안전장치: 이전 값 기억
            old_profit, old_win = get_performance(page)

            # --- 값 입력 (정확한 Index 4, 42, 43 사용) ---
            
            # 1. 분석 길이 (Index 4)
            inputs[PARAMS["len"]["index"]].fill(str(p_len))
            time.sleep(0.1)
            
            # 2. 손절 트리거 (Index 42)
            inputs[PARAMS["sl_trigger"]["index"]].fill(f"{p_sl:.1f}")
            time.sleep(0.1)
            
            # 3. 익절 트리거 (Index 43)
            inputs[PARAMS["tp_trigger"]["index"]].fill(f"{p_tp:.1f}")
            time.sleep(0.1)

            # 적용 및 대기
            page.keyboard.press("Enter")
            
            # 충분한 대기 시간 (6초)
            time.sleep(6.0)
            
            # 결과 확인
            new_profit, new_win = get_performance(page)
            
            # 값이 안 변했으면 한번 더 확인
            if new_profit == old_profit and new_win == old_win:
                time.sleep(2.0)
                new_profit, new_win = get_performance(page)
            
            print(f"   👉 결과: 순익 ${new_profit} | 승률 {new_win}%")

            return new_profit

        except Exception as e:
            print(f"⚠️ 에러: {e}")
            return -999999

if __name__ == "__main__":
    print("🚀 핵심 3대장(길이, 손절트리거, 익절트리거) 최적화 시작")
    
    study = optuna.create_study(
        study_name=STUDY_NAME,
        storage=DB_URL, 
        direction="maximize",
        load_if_exists=True
    )
    
    print(f"📂 DB 로드 완료. 현재 실험 수: {len(study.trials)}")
    
    # 1000번 촘촘하게 돌리기
    study.optimize(objective, n_trials=1000)