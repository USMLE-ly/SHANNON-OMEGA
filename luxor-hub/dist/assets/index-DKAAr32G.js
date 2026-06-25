import { r as reactExports, a as React } from "./index-8UqE6Xjs.js";
import { b as useLayoutEffect2 } from "./index-BGmLQ8S9.js";
var useReactId = React[" useId ".trim().toString()] || (() => void 0);
var count = 0;
function useId(deterministicId) {
  const [id, setId] = reactExports.useState(useReactId());
  useLayoutEffect2(() => {
    setId((reactId) => reactId ?? String(count++));
  }, [deterministicId]);
  return id ? `radix-${id}` : "";
}
export {
  useId as u
};
