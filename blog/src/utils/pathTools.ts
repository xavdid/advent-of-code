// currently unused
export const pathToBreadcrumbs = (
  url?: string
): { page: string; path?: string[] } => {
  if (!url || url == "/") {
    return { page: "" };
  }

  const pathSegments = url.slice(1).split("/").filter(Boolean);
  const page = pathSegments.slice(-1)[0];
  const path = pathSegments.slice(0, -1);

  return { page, path: path.length === 0 ? undefined : path };
};
