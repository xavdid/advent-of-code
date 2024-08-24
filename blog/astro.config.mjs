import { rehypeHeadingIds } from "@astrojs/markdown-remark";
import sitemap from "@astrojs/sitemap";
import expressiveCode from "astro-expressive-code";
import { defineConfig } from "astro/config";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeExternalLinks from "rehype-external-links";

// https://astro.build/config
export default defineConfig({
  site: "https://advent-of-code.xavd.id",
  markdown: {
    rehypePlugins: [
      rehypeHeadingIds,
      [
        rehypeExternalLinks,
        {
          target: "_blank",
          // content: {
          //   type: "element",
          //   tagName: "span",
          //   properties: { className: ["external-link-icon"] },
          //   children: [{ type: "text", value: " ↗" }],
          // },
        },
      ],
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
