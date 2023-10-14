import { getCollection } from "astro:content";

// https://docs.astro.build/en/guides/content-collections/#filtering-collection-queries
export const getPublishedWriteups = async () =>
  getCollection("writeups", ({ data: { draft } }) =>
    import.meta.env.PROD ? draft !== true : true
  );
