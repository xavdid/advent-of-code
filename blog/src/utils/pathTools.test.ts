import { expect, test } from "vitest";
import { pathToBreadcrumbs } from "./pathTools";

test("non-markdown pages have no breadcrumbs", () => {
  const { page, path } = pathToBreadcrumbs();

  expect(page).toEqual("");
  expect(path).toBeUndefined();
});

test("homepage has no breadcrumbs", () => {
  const { page, path } = pathToBreadcrumbs("/");

  expect(page).toEqual("");
  expect(path).toBeUndefined();
});

test("about page has a path", () => {
  const { page, path } = pathToBreadcrumbs("/about");

  expect(page).toEqual("about");
  expect(path).toBeUndefined();
});

test("writeup with year would have a path", () => {
  const { page, path } = pathToBreadcrumbs("/writeups/2022");

  expect(page).toEqual("2022");
  expect(path).toEqual(["writeups"]);
});

test("concepts have breadcrumbs", () => {
  const { page, path } = pathToBreadcrumbs("/concepts/depth-first-search");

  expect(page).toEqual("depth-first-search");
  expect(path).toEqual(["concepts"]);
});
