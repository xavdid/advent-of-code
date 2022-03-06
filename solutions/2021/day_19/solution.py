# prompt: https://adventofcode.com/2021/day/19
# code adapted from: https://gist.github.com/p88h/10f42de0f1add9e60c9e431247ef11f0

from collections import Counter
from itertools import product
from typing import Optional, Set, Tuple, List, cast
from pprint import pprint

from ...base import TextSolution, answer

Point3D = Tuple[int, int, int]


def try_align(
    source_scanner: List[Point3D], possible_overlapping_scanner: List[Point3D]
) -> Tuple[List[Point3D], Point3D]:
    aligned_dim_values: List[List[int]] = []
    # the offset betwee the source and possible match, if matched
    offsets: List[int] = []
    # once we've matched a destination column, skip it
    found_dimensions: Set[int] = set()
    for source_dim in range(3):
        # does 1 column at a time
        source_dim_values = [b[source_dim] for b in source_scanner]
        aligned_dim_offset = dest_dim = None  # the output of the counter
        candidate_dim_values: List[int] = []
        num_shared_beacons = 0
        for (dest_dim, signed_int) in [
            (0, 1),
            (1, 1),
            (2, 1),
            (0, -1),
            (1, -1),
            (2, -1),
        ]:
            # bail early if we have already seen a successful find in this dimension
            if dest_dim in found_dimensions:
                continue
            print(
                f"  comparing {source_dim=} with {dest_dim=}{' (I)' if signed_int == -1 else ''}"
            )

            candidate_dim_values = [
                b[dest_dim] * signed_int for b in possible_overlapping_scanner
            ]
            # A - B = C
            # -686 - (-618) == -68 (offset)
            differences = [
                source_val - candidate_val
                for source_val, candidate_val in product(
                    source_dim_values, candidate_dim_values
                )
            ]
            # pprint(
            #     list(zip(product(source_dim_values, candidate_dim_values), differences))
            # )
            c = Counter(differences)
            # pprint(c)
            assert c
            aligned_dim_offset, num_shared_beacons = c.most_common(1)[0]
            print(
                f"    got {num_shared_beacons} beacons at offset {aligned_dim_offset}"
            )
            # TODO: maybe remove common_offset check
            if num_shared_beacons >= 12:
                print("    found enough!")
                # found a valid match, quit early
                break

        if num_shared_beacons < 12:
            print("  no overlap")
            # failed to find sufficient overlap between these scanners
            return [], tuple()  # pyright bug, should be a type error

        # these all hold their last value from the loop when we break
        # they need to have been set to non-initial values
        assert aligned_dim_offset is not None
        assert num_shared_beacons
        assert dest_dim is not None
        assert candidate_dim_values

        found_dimensions.add(dest_dim)
        # B + C = A
        # -686 + 68 = -618
        aligned_dim_values.append(
            [v + aligned_dim_offset for v in candidate_dim_values]
        )
        # found_point_values.append([candidate_val - (candidate_val - source_val) for v in candidate_dim_values])
        offsets.append(aligned_dim_offset)

    assert len(aligned_dim_values) == 3
    assert len(offsets) == 3
    points = cast(List[Point3D], list(zip(*aligned_dim_values)))
    return points, tuple(offsets)


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

    @answer((79, 3621))
    # @answer((496, 14478))
    def solve(self) -> Tuple[int, int]:
        # self.pp(
        #     "\ngot",
        #     try_align(
        #         [(0, 2, 0), (1, 1, 0), (2, 0, 0), (3, -1, 0)],
        #         [(-4, 3, 0), (-3, 2, 0), (-2, 1, 0), (-1, 0, 0)],
        #         matches_needed=4,
        #     ),
        # )
        # self.pp(
        #     "\ngot",
        #     try_align(
        #         [(0, 2, 0), (1, 1, 0), (2, 0, 0), (3, -1, 0)],
        #         [(0, 1, 0), (1, 2, 0), (2, 3, 0), (3, 4, 0)],
        #         matches_needed=4,
        #     ),
        # )
        # return

        scanners = self.parse_input()

        beacons = set()
        # scanner 0 is always aligned
        aligned_scanner_reports = [scanners[0]]
        unmatched_scanners = scanners[1:]
        scanner_locations: List[Point3D] = [(0, 0, 0)]
        while aligned_scanner_reports:
            source = aligned_scanner_reports.pop()
            # self.pp(f"scanning block starting w/ ")
            next_round = []
            for potential_overlap in unmatched_scanners:
                self.pp(f"\naligning {source[0][0]} with {potential_overlap[0][0]}")
                aligned_points, scanner_location = try_align(source, potential_overlap)
                self.pp(
                    f"  got {len(aligned_points) if aligned_points else '0'} newly-aligned points"
                )
                if not aligned_points:
                    next_round.append(potential_overlap)
                    continue

                self.pp(f"{potential_overlap[0][0]} is now {aligned_points[0][0]}")
                self.pp(aligned_points, scanner_location)
                scanner_locations.append(scanner_location)
                aligned_scanner_reports.append(aligned_points)

            unmatched_scanners = next_round
            beacons.update(source)

        # self.pp(sorted(beacons))

        sxs = product(scanner_locations, repeat=2)
        # TODO: cleanup
        farthest_scanners = max(sum(abs(a - b) for (a, b) in zip(l, r)) for l, r in sxs)
        return len(beacons), farthest_scanners
