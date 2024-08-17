# prompt: https://adventofcode.com/2019/day/8

from ...base import BaseSolution


def chunked_list(list_, num_chunks, chunk_size):
    for chunk in range(num_chunks):
        yield list_[chunk * chunk_size : (chunk + 1) * chunk_size]


def prominent_color(stack):
    for pixel in stack:
        if pixel == "2":
            continue
        return pixel
    return None


class Solution(BaseSolution):
    _year = 2019
    _day = 8

    def solve(self):
        width = 25
        height = 6
        page_size = width * height

        min_zeroes = 999
        result = None
        chunks = []
        for chunk in chunked_list(self.input, len(self.input) // page_size, page_size):
            chunks.append(chunk)
            num_zeroes = chunk.count("0")
            res = chunk.count("1") * chunk.count("2")
            if num_zeroes < min_zeroes:
                result = res
                min_zeroes = num_zeroes

        raw_image = [prominent_color(x) for x in zip(*chunks)]
        image = [
            "".join(row).replace("0", ".")
            for row in chunked_list(raw_image, height, width)
        ]

        return (result, "\n" + "\n".join(image))
