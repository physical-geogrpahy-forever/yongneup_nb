# PB4Studio CHELSA21K archive

용늪 PB4Studio의 현재 CHELSA-TraCE21k forcing, 실행 패키지, 모델 프로세스 설명을 함께 보존하는 디렉터리다.

핵심 파일:

- `PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md`: 데이터, 모델 계보, coupling 프로세스, static/dynamic 및 original/modified 비교 설계
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv`: 21–0 ka, 100년 간격 211시점 CHELSA/EnviCloud 원자료
- `data/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.zip`: 위 CSV의 원본 압축본
- `payload/`: `PB4Studio_v6.6.3_CHELSA21K.zip`의 base64 분할 보존본
- `reconstruct_pb4.py`: PB4 ZIP 재구성 및 SHA-256 검증
- `SHA256SUMS.txt`: 원자료와 모델 패키지 무결성 값

과거 Beyer 실행 정확도나 이전 hotfix 정확도는 현재 CHELSA21K 결과로 간주하지 않는다. 새 결과는 동일 CHELSA21K forcing으로 다시 실행한 뒤 별도로 기록한다.