import { j as jsxRuntimeExports } from "./index-8UqE6Xjs.js";
import { j } from "./AppContent-BfL1bDTu.js";
import { T as Toaster$1 } from "./index-Dhopwi6u.js";
import { t } from "./index-Dhopwi6u.js";
const Toaster = ({ ...props }) => {
  const { theme = "system" } = j();
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    Toaster$1,
    {
      theme,
      className: "toaster group",
      toastOptions: {
        classNames: {
          toast: "group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-muted-foreground",
          actionButton: "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
          cancelButton: "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground"
        }
      },
      ...props
    }
  );
};
export {
  Toaster,
  t as toast
};
