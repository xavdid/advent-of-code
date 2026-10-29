import { glob } from "astro/loaders";
import { z } from "astro/zod";
import { defineCollection } from "astro:content";

const isProdBuild = import.meta.env.PROD;

const prodOnlyRule = (c: boolean) => (isProdBuild ? c : true);

const writeups = defineCollection({
  loader: glob({ base: "./src/content/writeups", pattern: "**/*.md" }),
  schema: z.object({
    title: z.string().refine((t) => prodOnlyRule(t !== "TKTK"), {
      message: "Missing post title during production build",
    }),
    day: z.number().gte(1).lte(25),
    year: z.number().gte(2015),
    pub_date: z.iso.date().optional(),
    concepts: z.optional(z.array(z.string())), // basically true or undefined
  }),
});

export const collections = { writeups };
