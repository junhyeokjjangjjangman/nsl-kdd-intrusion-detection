# NSL-KDD 기반 네트워크 침입 탐지 시스템 (IDS) 파이프라인

본 프로젝트는 대규모 네트워크 트래픽 데이터셋인 NSL-KDD를 활용하여 정상 트래픽과 해킹(공격) 트래픽을 정교하게 이진 분류하는 머신러닝 파이프라인 시스템임. 데이터 과학 5조의 텀프로젝트 결과물로, 데이터 전처리부터 최적 모델 최적화 및 오픈소스 SW 규격화를 달성함.

## 1. Installation & Usage

### 가상환경 구축 및 패키지 설치

로컬 PC 환경에 독립적인 가상환경을 설정하고 프로젝트 의존성 라이브러리를 일괄 설치함.

```bash
# 1. 가상환경 생성 (.venv)
python -m venv .venv

# 2. 가상환경 활성화 (Windows PowerShell 환경)
.venv\Scripts\Activate.ps1

# 3. 필수 패키지 일괄 설치
pip install -r requirements.txt

```

### 파이프라인 실행

```bash
# 4. 엔드투엔드 파이프라인 소스코드 통합 실행
python code/ids_proiect_final.py

```

---

## 2. 엔드투엔드 파이프라인 아키텍처 (End-to-End Pipeline)

전체 빅데이터 처리 공정은 단일 데이터 흐름 시스템으로 유기적으로 연결됨.

1. 데이터셋 로드 및 품질 검증 (Data Inspection): KDDTrain+.txt 및 KDDTest+.txt 데이터를 Pandas 기반으로 로드함. 데이터 크기(Train: 125,973행, Test: 22,544행) 및 결측치, 이상치, 클래스 불균형 등 데이터 품질 요소를 다각도로 검정함.
2. 레이블 이진화 (Label Binarization): 다중 클래스로 구성된 공격 유형을 정상 트래픽(0)과 해킹 트래픽(1)으로 이진화 처리함.
3. 컬럼별 전처리 변환기 (Column Transformer): 수치형 피처와 범주형 피처를 분리하여 맞춤형 전처리를 동시 실행함. 수치형 데이터는 SimpleImputer 및 StandardScaler를 통과시키고, 문자열 범주형 데이터는 OneHotEncoder를 통해 고차원 수치 벡터로 변환함.
4. 하이퍼파라미터 반복 실험 (Hyperparameter Tuning): Decision Tree 알고리즘의 max_depth와 criterion 옵션을 조합한 총 12가지 실험 알고리즘을 자동화 루프로 비교 분석함. 최고 F1-score를 기록한 조합을 베스트 모델로 강제 채택함.
5. 교차 검증 및 평가 (Robust Evaluation): 채택된 최종 모델을 대상으로 데이터 레이블 비율을 보존하는 5-Fold StratifiedKFold 교차 검증을 수행하여 일반화 성능을 입증함.
6. 시각화 및 결과 파일 자동 저장 (Outputs): 최종 산출물(오차 행렬, 피처 중요도 분석 그래프, CSV 성능 평가표)을 지정된 outputs/ 폴더 내에 이미지와 파일로 영구 저장함.

---

## 3. 핵심 오픈소스 함수 명세서 (API Specification)

교수님 지침 요건에 의거하여, 본 프로젝트의 모든 전처리 및 머신러닝 프로세스를 관장하는 최상위 단일 함수를 Scikit-learn 공식 문서 스타일로 규격화하여 선언함.

### run_ids_pipeline()

Description

* Execute the complete end-to-end Network Intrusion Detection System (IDS) workflow.

Parameters

* None
* 본 함수는 독립형 모듈 파이프라인으로, 실행 시 내부적으로 고정된 로컬 데이터 경로(data/KDDTrain+.txt, data/KDDTest+.txt)를 참조하여 구동됨.

Returns

* None
* 별도의 실행 객체를 반환하지 않고, 수치 레포트 및 시각화 플롯 결과물을 로컬 디렉터리(outputs/)에 파일로 직접 쓰기 처리를 수행함.

Output Artifacts (Generated Files)

* outputs/decision_tree_experiment_results.csv : 하이퍼파라미터 조합별 실험 데이터 세부 수치 표
* outputs/cross_validation_results.csv : 5-Fold 교차 검증 개별 스코어 및 평균치 데이터
* outputs/confusion_matrix_best_decision_tree.png : 베스트 모델의 오차 행렬 시각화 그래프
* outputs/feature_importance.csv : 원-핫 인코딩 컬럼이 포함된 전체 피처별 중요도 랭킹 수치
* outputs/feature_importance_top20.png : 분류 예측에 가장 기여도가 높은 상위 20개 피처 바 차트

---

## 4. 저장소 디렉터리 구조 (Repository Structure)

```text
├── data/
│   ├── KDDTrain+.txt          # 모델 학습용 NSL-KDD 원본 데이터
│   └── KDDTest+.txt           # 모델 검증용 NSL-KDD 원본 데이터
├── code/
│   └── ids_proiect_final.py   # 전처리, 모델링, 평가 통합 최상위 소스코드
├── outputs/                   # 코드 실행 시 자동 생성되는 최종 산출물 폴더
│   ├── decision_tree_experiment_results.csv
│   ├── cross_validation_results.csv
│   ├── confusion_matrix_best_decision_tree.png
│   ├── feature_importance.csv
│   └── feature_importance_top20.png
├── requirements.txt           # 가상환경 구축용 라이브러리 의존성 명세 파일
└── README.md                  # 본 시스템 사용 매뉴얼 및 제품 명세서

```

---

## 5. 최종 분석 결과 요약 (Key Findings)
일반화 성능 검증 수치: 5-Fold 교차 검증 결과, 최종 평균 F1-score 96.7%를 기록하여 초기 제안서 목표치에 부합하는 고성능 안정성을 증명함.
보안 실무 관점의 피처 해석: 특성 중요도 분석 결과, 출발지에서 목적지로 보내는 바이트 크기를 뜻하는 src_bytes 피처의 중요도가 약 0.706으로 지배적인 영향력을 행사함이 밝혀짐. 이는 비정상적인 대용량 페이로드 주입 및 네트워크 스캔 공격을 탐지하는 실제 사이버 보안 시스템의 탐지 메커니즘과 일치하는 유의미한 데이터 과학적 성과임.
