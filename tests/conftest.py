import sys
from unittest.mock import MagicMock

# 단위 테스트는 DB 연결이 불필요하므로 import 시점의 create_engine 호출 차단
sys.modules["app.core.db"] = MagicMock()
