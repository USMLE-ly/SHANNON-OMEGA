import { j as jsxRuntimeExports } from "./index-lXDoXHD3.js";
import { j } from "./AppContent-DVSg3RbM.js";
import { T as Toaster$1 } from "./index-CO4_u4nU.js";
import { t } from "./index-CO4_u4nU.js";
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
