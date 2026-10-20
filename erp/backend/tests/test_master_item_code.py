from app.services.master_item_code import item_code_series, next_code_from_existing, swatch_color_label


def test_pu_and_suede_share_fg_sequence():
    assert item_code_series("PU") == ("FG", 5)
    assert item_code_series("Suede") == ("FG", 5)
    assert item_code_series("SubKon") == ("SUB", 4)


def test_next_fg_follows_highest_number_not_text_order():
    codes = ["FG00001", "FG06427", "FG00999", "TEST123", "SUB0671"]
    assert next_code_from_existing(codes, "FG", 5) == "FG06428"


def test_next_sub_uses_its_own_series():
    codes = ["SUB0001", "SUB0671", "FG06427"]
    assert next_code_from_existing(codes, "SUB", 4) == "SUB0672"


def test_odd_padding_does_not_widen_the_series():
    codes = ["FG06427", "FG002816"]
    assert next_code_from_existing(codes, "FG", 5) == "FG06428"


def test_swatch_color_label_keeps_code_in_parentheses():
    assert swatch_color_label("OAK LEAF GREEN", "NB-F20-3458") == "OAK LEAF GREEN (NB-F20-3458)"


def test_next_code_starts_at_one_when_empty():
    assert next_code_from_existing([], "FG", 5) == "FG00001"
    assert next_code_from_existing([], "SUB", 4) == "SUB0001"
