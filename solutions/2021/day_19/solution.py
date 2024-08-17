# prompt: https://adventofcode.com/2021/day/19
# code adapted from: https://gist.github.com/p88h/10f42de0f1add9e60c9e431247ef11f0

from collections import Counter
from itertools import product
from typing import List, Optional, Set, Tuple, cast

from ...base import TextSolution, answer

Point3D = Tuple[int, int, int]


def align_scanner_reports(
    source_scanner: List[Point3D], target_scanner: List[Point3D]
) -> Tuple[List[Point3D], Optional[Point3D]]:
    """
    Given a pair of scanner reports, attempt to orient the second in terms of the first.

    We'll do each dimension independently.

    Only works if there are at least 12 beacons that show up in both reports.

    Returns the adjusted target points, plus their offset (from source -> target)
    """
    # if it's a match, we'll build 3 lists of adjusted values
    aligned_target_values: List[List[int]] = []
    # the offset between the source and possible match, if matched
    target_coordinates: List[int] = []
    # once we've matched a destination column, skip it
    found_dims: Set[int] = set()

    # check each of x, y, z values independently
    for source_dim in range(3):
        # pre-assign anything we'll set in the loops below
        target_dim_values: List[int] = []
        num_shared_beacons = -1
        difference = target_dim = None

        source_dim_values = [b[source_dim] for b in source_scanner]
        for signed_int, target_dim in product((1, -1), range(3)):
            # bail early if we have already seen a successful match in this dimension
            if target_dim in found_dims:
                continue

            target_dim_values = [b[target_dim] * signed_int for b in target_scanner]
            # S - T = D
            # -686 - (-618) == -68 (offset)
            differences = [
                source_val - target_val
                for source_val, target_val in product(
                    source_dim_values, target_dim_values
                )
            ]

            difference, num_shared_beacons = Counter(differences).most_common(1)[0]
            if num_shared_beacons >= 12:
                # found a valid match, stop checking other transforms
                break

        # failed to find sufficient overlap between these scanners
        if num_shared_beacons < 12:
            return [], ()

        # these all hold their last value from the loop when we break
        # they need to have been set to non-initial values
        assert target_dim_values
        assert difference is not None
        assert target_dim is not None

        found_dims.add(target_dim)
        # T + D = S
        # -686 + 68 = -618
        aligned_target_values.append(
            [target_val + difference for target_val in target_dim_values]
        )
        target_coordinates.append(difference)

    # after finding matches in all 3 dimensions, we have a new set of aligned points
    assert len(aligned_target_values) == 3
    assert len(target_coordinates) == 3

    points = cast(List[Point3D], list(zip(*aligned_target_values)))
    return points, tuple(target_coordinates)


class Solution(TextSolution):
    _year = 2021
    _day = 19

    def parse_input(self) -> List[List[Point3D]]:
        """
        Parses each individual scanner block into a list of tuples

        ```
        --- scanner 0 ---
        404,-588,-901
        528,-643,409
        ...

        --- scanner 1 ---
        686,422,578
        605,423,415
        ...
        ```

        becomes

        ```
        [
            [
                (404, -588,-901),
                (528, -643, 409),
                ...
            ],
            [
                (686, 422, 578),
                (605, 423, 415),
                ...
            ],
        ]
        ```
        """
        return [
            [tuple(map(int, line.split(","))) for line in block.split("\n")[1:]]
            for block in self.input.split("\n\n")
        ]

    @answer((496, 14478))
    def solve(self) -> Tuple[int, int]:
        scanners = self.parse_input()

        beacons: Set[Point3D] = set()
        # scanner 0 is always aligned
        aligned_scanner_reports = [scanners[0]]
        unaligned_scanners = scanners[1:]
        scanner_locations: List[Point3D] = [(0, 0, 0)]

        # we check each aligned scanner against unaligned reports to identify new beacons
        while aligned_scanner_reports:
            source = aligned_scanner_reports.pop()
            needs_recheck = []
            for target in unaligned_scanners:
                aligned_target, scanner_location = align_scanner_reports(source, target)

                if not (aligned_target and scanner_location):
                    needs_recheck.append(target)
                    continue

                scanner_locations.append(scanner_location)
                aligned_scanner_reports.append(aligned_target)

            unaligned_scanners = needs_recheck
            beacons.update(source)

        # scanner_pairs =

        farthest_scanners = max(
            sum(abs(a_dim - b_dim) for a_dim, b_dim in zip(A, B))
            for A, B in product(scanner_locations, repeat=2)
        )
        return len(beacons), farthest_scanners
