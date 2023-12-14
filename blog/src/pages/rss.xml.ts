import rss from "@astrojs/rss";
import type { APIRoute } from "astro";

import { getPublishedWriteups } from "../utils/collections";

export const GET: APIRoute = async (context) => {
  const writeups = await getPublishedWriteups();

  return rss({
    title: "@xavdid does Advent of Code",
    description:
      "Step-by-step puzzle explanations, written in Python, for Advent of Code puzzles.",
    site: context.site!,
    items: writeups
      .sort(
        (a, b) =>
          // these are only the published posts
          new Date(b.data.pub_date!).valueOf() -
            new Date(a.data.pub_date!).valueOf() ||
          // presume I did these in order in case of ties
          b.data.day - a.data.day
      )
      .map(({ slug, data: { year, day, title, pub_date } }) => {
        return {
          title: `David's AoC ${year} Day ${day} Solution`,
          link: `/writeups/${slug}`,
          description: `David solves: ${title}`,
          pubDate: new Date(pub_date!),
        };
      }),
  });
};
