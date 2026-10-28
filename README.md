# 나만의 용돈 기입장 (Budget Project)

Python 표준 라이브러리를 활용하여 개발한 CLI(Command Line Interface) 기반 용돈 기입장 프로그램입니다.

수입과 지출을 기록하고, 카테고리별로 거래 내역을 관리하며, 월별 통계와 예산 사용 현황을 확인할 수 있습니다. 거래 내역은 JSONL 파일로 저장하고 CSV 파일로 가져오거나 내보낼 수 있습니다.

## 1. 개발 환경

- 언어: Python 3.12
- 개발 도구: Visual Studio Code
- 실행 환경: macOS 터미널
- 사용 라이브러리: Python 표준 라이브러리
- 데이터 저장 방식: JSONL
- 테스트 프레임워크: unittest

별도의 외부 패키지 설치 없이 실행할 수 있습니다.

## 2. 주요 기능

| 기능 | 설명 |
|---|---|
| 거래 등록 | 날짜, 수입·지출 유형, 카테고리, 금액, 메모, 태그 입력 |
| 거래 조회 | 최근 거래 내역 조회 및 출력 개수 제한 |
| 거래 수정·삭제 | 거래 ID를 이용한 수정 및 삭제 |
| 카테고리 관리 | 카테고리 등록, 조회, 삭제 |
| 거래 검색 | 날짜, 유형, 카테고리, 금액, 키워드 조건 검색 |
| 월별 통계 | 총수입, 총지출, 잔액, 카테고리별 지출 계산 |
| 예산 관리 | 월별 카테고리 예산 설정 및 사용 현황 확인 |
| CSV 내보내기 | 저장된 거래 내역을 CSV 파일로 저장 |
| CSV 가져오기 | CSV 거래 내역 검증 및 중복 ID 건너뛰기 |
| 실행 시간 측정 | 데코레이터를 이용한 검색·통계 함수 실행 시간 출력 |

## 3. 프로젝트 구조

```text
Codyssey_B2-1_budget-project/
├── budget_app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   ├── decorators.py
│   ├── importer.py
│   └── exporter.py
├── data/
│   ├── transactions.jsonl
│   ├── categories.jsonl
│   └── budgets.jsonl
├── exports/
├── tests/
│   ├── test_service.py
│   ├── test_csv.py
│   └── test_decorators.py
├── .gitignore
└── README.md
```

`data/`의 JSONL 파일은 실행 과정에서 생성·관리되며, 개인 거래 데이터가 GitHub에 업로드되지 않도록 `.gitignore`에서 제외합니다.

## 4. 실행 방법

### 저장소 복제

```bash
git clone https://github.com/HsBin/Codyssey_B2-1_budget-project.git
cd Codyssey_B2-1_budget-project
```

### Python 버전 확인

```bash
python3.12 --version
```

Python 3.12 환경을 기준으로 작성했습니다.

### 전체 명령어 확인

```bash
python3.12 -m budget_app --help
```

## 5. 기능별 사용 방법

### 5.1 카테고리 관리

거래를 등록하기 전에 카테고리를 먼저 추가합니다.

```bash
python3.12 -m budget_app category add
```

실행 후 카테고리명을 입력합니다.

```text
카테고리명: food
[저장 완료] category=food
```

카테고리 목록 조회:

```bash
python3.12 -m budget_app category list
```

카테고리 삭제:

```bash
python3.12 -m budget_app category remove
```

### 5.2 거래 등록

```bash
python3.12 -m budget_app add
```

명령어 실행 후 날짜, 수입·지출 유형, 카테고리, 금액, 메모, 태그를 입력합니다.

### 5.3 거래 조회

```bash
python3.12 -m budget_app list --limit 5
```

최근 거래 내역을 최대 5건 조회합니다.

### 5.4 거래 수정

```bash
python3.12 -m budget_app update --id TX-거래ID
```

거래 ID를 지정한 후 수정할 항목을 입력합니다.

### 5.5 거래 삭제

```bash
python3.12 -m budget_app delete --id TX-거래ID
```

거래 ID를 지정하여 삭제합니다.

### 5.6 거래 검색

카테고리별 검색:

```bash
python3.12 -m budget_app search --category food
```

날짜별 검색:

```bash
python3.12 -m budget_app search --from 2026-10-01 --to 2026-10-31
```

금액 범위 검색:

```bash
python3.12 -m budget_app search --min-amount 5000 --max-amount 20000
```

여러 검색 조건을 함께 지정할 수도 있습니다.

### 5.7 월별 통계

```bash
python3.12 -m budget_app summary --month 2026-10
```

해당 월의 총수입, 총지출, 잔액, 카테고리별 지출을 확인합니다.

### 5.8 예산 관리

월별 카테고리 예산 설정:

```bash
python3.12 -m budget_app budget set
```

월별 예산 사용 현황 조회:

```bash
python3.12 -m budget_app budget list --month 2026-10
```

예산과 실제 지출을 비교하여 사용률과 잔여 금액을 계산하며, 예산을 초과하면 경고를 표시합니다.

### 5.9 CSV 내보내기

```bash
python3.12 -m budget_app export --output exports/transactions.csv
```

거래 내역을 CSV 파일로 저장합니다.

### 5.10 CSV 가져오기

```bash
python3.12 -m budget_app import --input exports/transactions.csv
```

CSV 데이터를 검사한 뒤 거래 내역을 가져옵니다.

이미 등록된 거래 ID는 중복 저장하지 않고 건너뜁니다. CSV에서 사용하는 카테고리는 미리 등록되어 있어야 합니다.

## 6. 데이터 저장 구조

데이터는 JSONL(JSON Lines) 형식으로 관리합니다.

JSONL은 한 줄에 하나의 JSON 객체를 저장하는 방식입니다.

거래 데이터 예시:

```json
{"id":"TX-000001","type":"expense","date":"2026-10-28","amount":15000,"category":"food","memo":"점심","tags":["meal"]}
```

주요 데이터 파일:

- `transactions.jsonl`: 거래 내역
- `categories.jsonl`: 카테고리
- `budgets.jsonl`: 월별 예산

거래 수정·삭제 등 일부 파일 갱신 작업에서는 임시 파일과 `os.replace()`를 사용하여 저장 과정의 안정성을 높였습니다.

## 7. 입력 검증 및 예외 처리

잘못된 데이터가 저장되지 않도록 입력값을 검증합니다.

검증 항목에는 다음이 포함됩니다.

- 날짜 및 월 형식
- 수입·지출 유형
- 금액의 유효성
- 등록된 카테고리 사용 여부
- 거래 ID 존재 여부
- 검색 금액 범위
- CSV 파일 존재 여부와 필수 열
- CSV 데이터의 유효성 및 중복 ID

오류가 발생하면 가능한 경우 Python의 긴 예외 출력 대신 사용자가 이해할 수 있는 메시지를 표시합니다.

예시:

```text
[오류] 최소 금액은 최대 금액보다 클 수 없습니다.
[오류] CSV 파일을 찾을 수 없습니다.
[오류] 2행: 금액은 0보다 커야 합니다.
```

## 8. 데코레이터 활용

`decorators.py`에 함수 실행 시간을 측정하는 `measure_time` 데코레이터를 구현했습니다.

`@wraps`를 사용하여 원래 함수의 이름과 메타데이터를 유지하며, `time.perf_counter()`로 실행 시간을 측정합니다.

거래 검색과 월별 통계 함수에 적용했습니다.

출력 예시:

```text
[실행 시간] get_monthly_summary: 0.0022초
```

## 9. 자동화 테스트

Python 표준 라이브러리의 `unittest`를 사용하여 기능을 검증합니다.

테스트 실행 명령어:

```bash
python3.12 -m unittest discover -s tests -v
```

테스트 대상:

- 거래 등록 및 입력값 검증
- 거래 수정·삭제·검색
- 월별 통계 계산
- 예산 관리 및 잘못된 금액 처리
- CSV 내보내기·가져오기
- CSV 중복 거래 처리
- 존재하지 않는 CSV 파일 처리
- 데코레이터 반환값 및 출력 검증

현재 총 **16개의 자동화 테스트가 통과**했습니다.

```text
Ran 16 tests in 0.028s

OK
```

테스트에서는 `tempfile.TemporaryDirectory()`를 활용하여 실제 사용자 데이터에 영향을 주지 않도록 임시 저장소를 사용합니다.

## 10. 사용 기술 및 학습 내용

- `argparse`: CLI 명령어와 옵션 처리
- `dataclasses`: 거래 데이터 모델 정의
- `json`: JSONL 데이터 직렬화 및 역직렬화
- `csv`: CSV 파일 가져오기 및 내보내기
- `pathlib`: 파일 및 디렉터리 경로 관리
- `tempfile`, `os.replace`: 안전한 파일 갱신
- `datetime`: 날짜 형식 검증
- `uuid`: 거래 ID 생성
- `heapq`: 최근 거래 내역 조회
- `functools.wraps`: 데코레이터 구현
- `time.perf_counter`: 실행 시간 측정
- `unittest`: 자동화 테스트

## 11. 프로젝트 저장소

GitHub: https://github.com/HsBin/Codyssey_B2-1_budget-project
