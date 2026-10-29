// @ts-check

import js from "@eslint/js";
import prettier from "eslint-config-prettier/flat";
import astro from "eslint-plugin-astro";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";

export default defineConfig(
  { ignores: ["dist/", ".astro/", "eslint.config.mjs"] },

  js.configs.recommended,
  tseslint.configs.recommended,
  astro.configs.recommended,
  prettier,
);
