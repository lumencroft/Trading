from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]

        # 설정창 찾기
        dialog = page.locator("div[data-name='indicator-properties-dialog']")
        if not dialog.is_visible():
            print("❌ 설정창을 열고 실행해주세요!")
            return

        inputs = dialog.locator("input").all()
        
        print("🧪 입력칸 테스트를 시작합니다. 화면을 잘 봐주세요!")
        
        # [테스트 범위] 의심가는 구간 (35번 ~ 50번)
        # 이 구간에 시드, 목표수익, 손절, 레버리지 등이 몰려있습니다.
        test_indices = range(35, 52) 

        for i in test_indices:
            try:
                # 체크박스(ON/OFF)는 건너뜁니다
                if inputs[i].get_attribute("type") == "checkbox":
                    print(f"   [Index {i}] 체크박스라 패스")
                    continue
                
                # 식별하기 쉬운 값 입력 (예: 1035, 1036...)
                marker_value = f"99{i}" 
                
                inputs[i].click()
                inputs[i].fill(marker_value)
                print(f"👉 Index {i}번에 값 '{marker_value}' 입력함")
                time.sleep(0.5) # 눈으로 확인할 시간 줌
            except:
                pass

        print("\n" + "="*50)
        print("🛑 화면 확인 타임!")
        print("설정창에 '9935', '9940' 같은 숫자들이 박혀있을 겁니다.")
        print("어떤 숫자가 '목표 수익' 칸에 들어갔는지,")
        print("어떤 숫자가 '손절 트리거' 칸에 들어갔는지 알려주세요.")
        print("="*50)

if __name__ == "__main__":
    run()