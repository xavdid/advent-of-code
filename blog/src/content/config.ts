import { defineCollection, z } from "astro:content";

const isProdBuild = import.meta.env.PROD;

const prodOnlyRule = (c: boolean) => (isProdBuild ? c : true);

const writeups = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string().refine((t) => prodOnlyRule(t !== "TKTK"), {
      message: "Missing post title during production build",
    }),
    day: z.number().gte(1).lte(25),
    year: z.number().gte(2015),
    // on newer Astro versions, can use z.string().date().optional()
    pub_date: z.optional(z.string().regex(/^\d{4}-\d{2}-\d{2}$/)),
    concepts: z.optional(z.array(z.string())), // basically true or undefined
  }),
});

export const collections = { writeups };
