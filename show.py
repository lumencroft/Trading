import optuna

# ==========================================
# [설정] 아까 돌린 코드와 똑같이 맞춰주세요
DB_URL = "sqlite:///trading_opt.db"
STUDY_NAME = "strategy_real_v2" 
# 만약 에러가 나면, 직전 코드의 STUDY_NAME이 뭔지 확인해보세요.
# (strategy_optimization_v1 일 수도 있습니다)
# ==========================================

def show_best():
    try:
        # DB에서 기록 불러오기
        study = optuna.load_study(study_name=STUDY_NAME, storage=DB_URL)
        
        print("\n" + "="*40)
        print(f"🏆 [최종 우승 설정] (Trial {study.best_trial.number})")
        print("="*40)
        print(f"💰 최대 순익: ${study.best_value}")
        print("-" * 20)
        print("🔧 세팅값:")
        
        params = study.best_params
        # 보기 좋게 출력
        print(f"   1. 분석 길이 (Len)     : {params.get('len')}")
        print(f"   2. 손절 트리거 (SL %)  : {params.get('sl_trigger')}%")
        print(f"   3. 익절 트리거 (TP %)  : {params.get('tp_trigger')}%")
        print("="*40)
        
        print("\n💡 바로 트레이딩뷰에 가서 입력하시면 됩니다.")

    except KeyError:
        print("❌ Study 이름을 못 찾았습니다. DB 파일이 있나 확인하거나 이름을 체크하세요.")

if __name__ == "__main__":
    show_best()