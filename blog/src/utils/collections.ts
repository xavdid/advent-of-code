import { getCollection, type CollectionEntry } from "astro:content";

export type Writeup = CollectionEntry<"writeups">;

// https://docs.astro.build/en/guides/content-collections/#filtering-collection-queries
// everything in dev, published only in prod
export const getPublishedWriteups = async () =>
  getCollection("writeups", ({ data: { pub_date } }) =>
    import.meta.env.PROD ? pub_date : true
  );

export const getWriteupsByYear = async () => {
  const writeups = await getPublishedWriteups();

  return writeups.reduce((result, writeup) => {
    if (!result.has(writeup.data.year)) {
      result.set(writeup.data.year, []);
    }

    result.get(writeup.data.year)?.push(writeup);

    return result;
  }, new Map<number, Writeup[]>());
};
