"""A 股涨跌停价规则（``eltdx.mac.price_rules``）的离线测试。

覆盖评审点出的两处规则错误：

1. 创业板代码段只写了 ``300`` / ``301``，漏了 2024 年启用的 ``302`` 段；
2. ST 判断排在板块判断之前，导致创业板 / 科创板 ST 被按主板 5% 计算
   （注册制板块对 ST 同样适用 20%）。
"""

from __future__ import annotations

import pytest

from eltdx.mac.price_rules import compute_price_limits, get_no_limit_window_days


class TestChiNextSegment:
    """创业板 300 / 301 / 302 一律 20%。"""

    @pytest.mark.parametrize("code", ["300001", "301001", "302001"])
    def test_chinext_codes_use_twenty_percent(self, code: str) -> None:
        up, down = compute_price_limits(0, code, "普通股票", 10.0)
        assert up == pytest.approx(12.0)
        assert down == pytest.approx(8.0)

    def test_302_segment_is_not_treated_as_main_board(self) -> None:
        """302 段若漏判会退回主板 10%，是最容易静默出错的一档。"""

        up, _ = compute_price_limits(0, "302001", "普通股票", 10.0)
        assert up != pytest.approx(11.0)

    def test_unassigned_30x_segment_is_not_guessed(self) -> None:
        """303/304 等未分配段不应被 ``startswith("30")`` 误判成创业板。"""

        up, _ = compute_price_limits(0, "303001", "普通股票", 10.0)
        assert up == pytest.approx(11.0)


class TestStPriority:
    """ST 只在主板下降到 5%；注册制板块的 ST 仍是 20%。"""

    def test_main_board_st_is_five_percent(self) -> None:
        up, down = compute_price_limits(0, "000001", "ST 平安", 10.0)
        assert up == pytest.approx(10.5)
        assert down == pytest.approx(9.5)

    def test_chinext_st_stays_twenty_percent(self) -> None:
        for code in ("300001", "301001", "302001"):
            up, down = compute_price_limits(0, code, "ST 某某", 10.0)
            assert up == pytest.approx(12.0), f"{code} 被误按 5% 计算"
            assert down == pytest.approx(8.0)

    def test_star_market_st_stays_twenty_percent(self) -> None:
        up, down = compute_price_limits(1, "688001", "*ST 某某", 10.0)
        assert up == pytest.approx(12.0)
        assert down == pytest.approx(8.0)

    def test_beijing_exchange_is_thirty_percent(self) -> None:
        up, down = compute_price_limits(2, "830001", "普通股票", 10.0)
        assert up == pytest.approx(13.0)
        assert down == pytest.approx(7.0)


class TestNoLimitWindow:
    """上市初期无涨跌幅窗口。"""

    @pytest.mark.parametrize("code", ["300001", "301001", "302001", "000001"])
    def test_first_five_days_have_no_limit(self, code: str) -> None:
        assert get_no_limit_window_days(0, code, "普通股票") == 5
        up, down = compute_price_limits(0, code, "普通股票", 10.0, listed_days=1)
        assert up is None and down is None

    def test_sixth_day_has_limit(self) -> None:
        up, _ = compute_price_limits(0, "302001", "普通股票", 10.0, listed_days=6)
        assert up == pytest.approx(12.0)

    def test_beijing_first_day_no_limit(self) -> None:
        assert get_no_limit_window_days(2, "830001", "普通股票") == 1


class TestIndexLike:
    """指数/板块类无涨跌停。"""

    def test_index_code_has_no_limit(self) -> None:
        up, down = compute_price_limits(1, "000001", "上证指数", 3000.0)
        assert up is None and down is None

    def test_invalid_pre_close_has_no_limit(self) -> None:
        assert compute_price_limits(0, "000001", "平安银行", 0.0) == (None, None)
