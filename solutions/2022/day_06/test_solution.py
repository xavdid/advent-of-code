import pytest
from solution import find_packet_start


@pytest.mark.parametrize(
    "data, result",
    [
        ("mjqjpqmgbljsphdztnvjfqwrcgsmlb", 7),
        ("bvwbjplbgvbhsrlpgdmjqwftvncz", 5),
        ("nppdvjthqldpwncqszvftbrmjlhg", 6),
        # expected to fail
        ("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg", 11),
        ("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw", 11),
    ],
)
def test_packet_start(data, result):
    assert find_packet_start(data, 4) == result
