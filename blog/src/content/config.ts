// 1. Import utilities from `astro:content`
import { defineCollection, z } from "astro:content";

// 2. Define a `type` and `schema` for each collection
const writeups = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(), // puzzle title
    day: z.number().gte(1).lte(25),
    year: z.number().gte(2015),
    pub_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    draft: z.optional(z.boolean()), // basically true or undefined
    concepts: z.optional(z.array(z.string())), // basically true or undefined
  }),
});

// 3. Export a single `collections` object to register your collection(s)
export const collections = { writeups };
