import { rehypeHeadingIds } from "@astrojs/markdown-remark";
import sitemap from "@astrojs/sitemap";
import { defineConfig } from "astro/config";
import rehypeAutolinkHeadings from "rehype-autolink-headings";

import expressiveCode from "astro-expressive-code";

// https://astro.build/config
export default defineConfig({
  site: "https://advent-of-code.xavd.id",
  markdown: {
    rehypePlugins: [
      rehypeHeadingIds,
      [
        rehypeAutolinkHeadings,
        {
          behavior: "wrap",
        },
      ],
    ],
  },
  integrations: [
    sitemap(),
    expressiveCode({
      themes: ["monokai"],
      frames: false,
      styleOverrides: {
        borderColor: "white",
        borderWidth: "1px",
        codeLineHeight: "1.4",
      },
    }),
  ],
});
