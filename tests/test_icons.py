from src.draw.icons import find_icon_file, get_file_icon


def markup(*args, **kwargs):
    return get_file_icon(*args, **kwargs).content


def test_icon_built_only_from_a_circle_still_draws():
    assert "<circle" in markup("circle")


def test_every_shape_in_an_icon_is_kept():
    globe = markup("globe")
    assert "<circle" in globe
    assert globe.count("<path") == 2


def test_unknown_name_falls_back_when_one_is_given():
    assert markup("no-such-icon", fallback="circle-dot") == markup("circle-dot")


def test_unknown_name_draws_nothing_without_a_fallback():
    assert markup("no-such-icon") == ""


def test_names_that_could_escape_the_icons_directory_are_refused():
    for name in ("../../conf", "/etc/passwd", "a/b", "Circle", ""):
        assert find_icon_file(name) is None
