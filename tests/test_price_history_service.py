from app.services.price_history_service import _change_rate, _total


class TestChangeRate:
    def test_normal(self):
        assert _change_rate(110, 100) == 0.1

    def test_decrease(self):
        assert _change_rate(90, 100) == -0.1

    def test_previous_is_none(self):
        assert _change_rate(100, None) is None

    def test_current_is_none(self):
        assert _change_rate(None, 100) is None

    def test_both_none(self):
        assert _change_rate(None, None) is None

    def test_previous_is_zero(self):
        # 0으로 나누면 None
        assert _change_rate(100, 0) is None


class TestTotal:
    def test_all_values(self):
        assert _total(100, 200, 300) == 600.0

    def test_partial_none(self):
        # None 항목은 합산에서 제외
        assert _total(100, None, 300) == 400.0

    def test_all_none(self):
        assert _total(None, None, None) is None
