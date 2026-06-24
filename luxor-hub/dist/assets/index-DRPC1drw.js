import { r as reactExports, a as React } from "./index-BFEQqA4N.js";
import { b as useLayoutEffect2 } from "./index-BaP5T_cd.js";
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
