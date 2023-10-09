// 1. Import utilities from `astro:content`
import { defineCollection, z } from "astro:content";

// 2. Define a `type` and `schema` for each collection
const solutions = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(), // puzzle title
    day: z.number().gte(1).lte(25),
    year: z.number().gte(2015),
  }),
});

// 3. Export a single `collections` object to register your collection(s)
export const collections = { solutions };
