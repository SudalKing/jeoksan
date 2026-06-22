from unittest.mock import MagicMock, patch
from etl.normalize import normalize_unit, ensure_unit_aliases


ALIAS_MAP = {"M": "m", "M2": "㎡", "ea": "개"}


class TestNormalizeUnit:
    def test_known_alias(self):
        assert normalize_unit("M", ALIAS_MAP) == "m"

    def test_strips_whitespace_before_lookup(self):
        assert normalize_unit("M ", ALIAS_MAP) == "m"
        assert normalize_unit(" M", ALIAS_MAP) == "m"

    def test_unknown_unit_just_return(self):
        assert normalize_unit("kg", ALIAS_MAP) == "kg"

    def test_none_returns_none(self):
        assert normalize_unit(None, ALIAS_MAP) is None


class TestEnsureUnitAliases:
    def test_skips_existing_aliases(self):
        session = MagicMock()
        existing = MagicMock()
        existing.raw_unit = "M"
        existing.canonical_unit = "m"
        session.query.return_value.all.return_value = [existing]

        with patch("etl.normalize.UnitAlias") as MockAlias:
            MockAlias.side_effect = lambda **kw: MagicMock(**kw)
            ensure_unit_aliases(session)

        added_raw_units = [call.kwargs.get("raw_unit") for call in MockAlias.call_args_list]
        assert "M" not in added_raw_units

    def test_inserts_missing_aliases(self):
        session = MagicMock()
        session.query.return_value.all.return_value = []

        with patch("etl.normalize.UnitAlias") as MockAlias:
            MockAlias.side_effect = lambda **kw: MagicMock(**kw)
            ensure_unit_aliases(session)

        assert session.add.called
        assert session.commit.called
