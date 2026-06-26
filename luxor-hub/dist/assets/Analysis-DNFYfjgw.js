import { e as useNavigate, r as reactExports, j as jsxRuntimeExports } from "./index-8UqE6Xjs.js";
import { A as AppLayout } from "./AppLayout-Cpw6ai4t.js";
import { e as useAuth, s as supabase, B as Button, T as TriangleAlert, R as RefreshCw } from "./AppContent-BfL1bDTu.js";
import { C as Card, a as CardContent, b as CardHeader, c as CardTitle } from "./card-jMBz4erV.js";
import { B as Badge } from "./badge-oDZIC4B0.js";
import { t as toast } from "./index-Dhopwi6u.js";
import { G as GlowingEffect } from "./glowing-effect-CNOYU396.js";
import { m as motion } from "./proxy-BwJSqjZP.js";
import { C as Camera } from "./camera-to52LeLP.js";
import { A as AnimatePresence } from "./index-CZvaVStM.js";
import { L as LoaderCircle } from "./loader-circle-B-ch7sWf.js";
import { S as Sparkles } from "./sparkles-CSm-T44U.js";
import { E as Eye } from "./eye-DmmE8jI3.js";
import { P as Palette } from "./palette-CyK0kL41.js";
import { S as ShieldCheck } from "./shield-check-JvXe0EgZ.js";
import { T as TrendingUp } from "./trending-up-BJime1xL.js";
import { L as Layers } from "./BottomNav-3LNFIPH1.js";
import { U as Upload } from "./upload-DmuO3iMl.js";
import { I as Instagram } from "./instagram-DahnFDoJ.js";
import { T as Twitter } from "./twitter-Bq1-DC-b.js";
import { E as ExternalLink } from "./external-link-DZx1N1ZF.js";
import "./index-BxC1Q5pe.js";
import "./shirt-C9gbE4N8.js";
function CircularScore({ score, size = 112 }) {
  const isNA = score === null || score === void 0 || score === 0;
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = isNA ? circ : circ - score / 100 * circ;
  const [animatedOffset, setOffset] = reactExports.useState(circ);
  reactExports.useEffect(() => {
    const id = setTimeout(() => setOffset(offset), 300);
    return () => clearTimeout(id);
  }, [score]);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative", style: { width: size, height: size }, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("svg", { width: size, height: size, className: "-rotate-90", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("defs", { children: /* @__PURE__ */ jsxRuntimeExports.jsxs("linearGradient", { id: "goldArc", x1: "0%", y1: "0%", x2: "100%", y2: "100%", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("stop", { offset: "0%", stopColor: "#C6A55C" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("stop", { offset: "100%", stopColor: "#E8D5A3" })
      ] }) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("circle", { cx: size / 2, cy: size / 2, r, fill: "none", stroke: "hsl(var(--muted))", strokeWidth: "6" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        motion.circle,
        {
          cx: size / 2,
          cy: size / 2,
          r,
          fill: "none",
          stroke: "url(#goldArc)",
          strokeWidth: "6",
          strokeLinecap: "round",
          strokeDasharray: circ,
          initial: { strokeDashoffset: circ },
          animate: { strokeDashoffset: isNA ? circ : animatedOffset },
          transition: { duration: 1.5, ease: "easeOut" }
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "absolute inset-0 flex flex-col items-center justify-center", children: [
      isNA ? /* @__PURE__ */ jsxRuntimeExports.jsx(
        motion.span,
        {
          className: "text-lg font-bold text-muted-foreground/40",
          initial: { opacity: 0 },
          animate: { opacity: 1 },
          transition: { duration: 0.5 },
          children: "N/A"
        }
      ) : /* @__PURE__ */ jsxRuntimeExports.jsx(jsxRuntimeExports.Fragment, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(
        motion.span,
        {
          className: "text-2xl font-bold gold-text",
          initial: { opacity: 0, scale: 0.5 },
          animate: { opacity: 1, scale: 1 },
          transition: { delay: 0.8, type: "spring" },
          children: score
        }
      ) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-[9px] text-muted-foreground -mt-1", children: "/ 100" })
    ] })
  ] });
}
function Footer() {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("footer", { className: "relative mt-12 mb-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute inset-0 -top-6 h-px bg-gradient-to-r from-transparent via-border to-transparent backdrop-blur-sm" }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "pt-6 flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground/60", children: "© 2026 LUXOR® — AI Fashion Style" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center gap-4", children: [
        { icon: Instagram, href: "#" },
        { icon: Twitter, href: "#" },
        { icon: ExternalLink, href: "#" }
      ].map(({ icon: Icon, href }, i) => /* @__PURE__ */ jsxRuntimeExports.jsx(
        motion.a,
        {
          href,
          whileHover: { scale: 1.15, y: -2 },
          whileTap: { scale: 0.9 },
          className: "w-8 h-8 rounded-full bg-muted/30 flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors",
          children: /* @__PURE__ */ jsxRuntimeExports.jsx(Icon, { className: "w-4 h-4" })
        },
        i
      )) })
    ] })
  ] });
}
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } }
};
const itemAnim = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } }
};
function InteractiveStylistQuiz({ imagePreview, styleName, actualColors }) {
  const [step, setStep] = reactExports.useState(0);
  const [answers, setAnswers] = reactExports.useState([]);
  const [chatHistory, setChatHistory] = reactExports.useState([]);
  const [loading, setLoading] = reactExports.useState(false);
  const [result, setResult] = reactExports.useState(null);
  const [nextQuestion, setNextQuestion] = reactExports.useState("Tell me what kind of vibe you are going for today? (Casual, Business, Party, Date Night, or Sport)");
  const [quizComplete, setQuizComplete] = reactExports.useState(false);
  const options = [
    ["Casual", "Business", "Party", "Date Night", "Sport"],
    ["Hot", "Mild", "Cold"],
    ["Neutrals", "Brights", "Pastels", "Dark"]
  ];
  const handleAnswer = async (answer) => {
    if (!imagePreview) {
      toast.error("Upload an image first");
      return;
    }
    const newAnswers = [...answers, answer];
    setAnswers(newAnswers);
    setStep(step + 1);
    setLoading(true);
    try {
      let b64 = imagePreview;
      if (b64.startsWith("data:")) b64 = b64.split(",")[1];
      else if (b64.startsWith("http")) {
        const r = await fetch(b64);
        const blob = await r.blob();
        b64 = await new Promise((res) => {
          const fr = new FileReader();
          fr.onloadend = () => res(fr.result.split(",")[1]);
          fr.readAsDataURL(blob);
        });
      }
      const newHistory = [...chatHistory, { role: "user", text: answer }];
      setChatHistory(newHistory);
      const api = "https://luxor.ly";
      const resp = await fetch(api + "/api/v1/stylist-explore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_b64: b64,
          chat_history: newHistory,
          answer,
          _t: Date.now()
        })
      });
      if (!resp.ok) throw new Error("Server error: " + resp.status);
      const data = await resp.json();
      if (data.generated_prompt && data.image_url) {
        setResult({
          image_url: data.image_url,
          generated_prompt: data.generated_prompt,
          outfit_name: data.outfit_name || "New Style"
        });
        setQuizComplete(true);
        setNextQuestion("");
        toast.success("New outfit created! ✨");
      } else if (data.next_question) {
        setNextQuestion(data.next_question);
        setChatHistory([...newHistory, { role: "assistant", text: data.next_question }]);
      }
    } catch (e) {
      toast.error(e.message);
      setStep(step);
    } finally {
      setLoading(false);
    }
  };
  const resetQuiz = () => {
    setStep(0);
    setAnswers([]);
    setChatHistory([]);
    setResult(null);
    setNextQuestion("Tell me what kind of vibe you are going for today? (Casual, Business, Party, Date Night, or Sport)");
    setQuizComplete(false);
  };
  const currentOptions = step < options.length ? options[step] : ["Yes", "No", "Try something different"];
  return /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: itemAnim, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative rounded-[1.5rem] border-[0.75px] border-border p-3", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(GlowingEffect, { spread: 50, glow: true, proximity: 64, inactiveZone: 0.01, borderWidth: 3 }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "glass-card border-0 shadow-none", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(CardHeader, { className: "pb-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(CardTitle, { className: "font-display flex items-center gap-2 text-lg", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-0.5 h-5 gold-gradient rounded-full mr-1" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-5 h-5 text-primary" }),
          " ✨ What other fashion would you like to explore?"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Answer a few questions and discover a completely new outfit." })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(CardContent, { className: "space-y-4", children: [
        !quizComplete && !loading && step === 0 && !result && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-center py-6", children: imagePreview ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-foreground/80", children: nextQuestion }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap justify-center gap-2", children: currentOptions.map((opt) => /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              variant: "outline",
              onClick: () => handleAnswer(opt),
              className: "bg-white/10 backdrop-blur-md border-primary/30 hover:bg-primary/20 hover:border-primary/50 transition-all text-sm px-5 py-2.5",
              children: opt
            },
            opt
          )) })
        ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center gap-3 text-muted-foreground", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "w-12 h-12" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm", children: "Upload an outfit photo above" })
        ] }) }),
        !quizComplete && loading && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-center py-10 space-y-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "h-10 w-10 animate-spin text-primary mx-auto" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-display text-base", children: "FASHION-OMEGA is crafting your look..." }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap justify-center gap-2", children: answers.map((a, i) => /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: "secondary", className: "text-xs", children: a }, i)) })
        ] }),
        !quizComplete && !loading && step > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-center py-4 space-y-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap justify-center gap-2 mb-4", children: answers.map((a, i) => /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: "secondary", className: "text-xs", children: a }, i)) }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-foreground/80", children: nextQuestion }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap justify-center gap-2", children: currentOptions.map((opt) => /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              variant: "outline",
              onClick: () => handleAnswer(opt),
              className: "bg-white/10 backdrop-blur-md border-primary/30 hover:bg-primary/20 hover:border-primary/50 transition-all text-sm px-5 py-2.5",
              children: opt
            },
            opt
          )) })
        ] }),
        quizComplete && result && /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.div, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, className: "space-y-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/20", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-5 h-5 text-primary flex-shrink-0" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-semibold text-foreground", children: result.outfit_name || "New Style" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground mt-1", children: result.generated_prompt })
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Eye, { className: "w-3.5 h-3.5" }),
                " Your Current Style"
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "rounded-2xl overflow-hidden border border-border shadow-lg bg-muted/20 aspect-[3/4]", children: /* @__PURE__ */ jsxRuntimeExports.jsx("img", { src: imagePreview, alt: "Current", className: "w-full h-full object-cover" }) }),
              styleName && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground text-center", children: styleName })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-3.5 h-3.5 text-primary" }),
                " ✨ New Style Inspiration"
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "rounded-2xl overflow-hidden border border-border shadow-lg bg-muted/20 aspect-[3/4]", children: /* @__PURE__ */ jsxRuntimeExports.jsx(
                "img",
                {
                  src: result.image_url,
                  alt: "New style",
                  className: "w-full h-full object-cover",
                  onError: (e) => {
                    e.target.style.display = "none";
                  }
                }
              ) })
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { variant: "outline", className: "text-[10px] text-muted-foreground", children: [
              "Based on your vibe: ",
              answers.join(" → ")
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { size: "sm", variant: "outline", onClick: resetQuiz, className: "border-primary/30 hover:bg-primary/10", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-3 h-3 mr-1" }),
              " Try Another Vibe"
            ] })
          ] })
        ] })
      ] })
    ] })
  ] }) });
}
function Analysis() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [imagePreview, setImagePreview] = reactExports.useState(null);
  const [imageFile, setImageFile] = reactExports.useState(null);
  const [data, setData] = reactExports.useState(null);
  const [loading, setLoading] = reactExports.useState(false);
  const [savedId, setSavedId] = reactExports.useState(null);
  const [analysisFailed, setAnalysisFailed] = reactExports.useState(false);
  const [saving, setSaving] = reactExports.useState(false);
  const [history, setHistory] = reactExports.useState([]);
  const fileRef = reactExports.useRef(null);
  const analyzeRef = reactExports.useRef(null);
  reactExports.useEffect(() => {
    analyzeRef.current = analyzeOutfit;
  });
  reactExports.useEffect(() => {
    if (imageFile && analyzeRef.current) {
      analyzeRef.current(imageFile);
    }
  }, [imageFile]);
  reactExports.useEffect(() => {
    const pending = sessionStorage.getItem("pendingUpload");
    if (pending) {
      sessionStorage.removeItem("pendingUpload");
      const byteString = atob(pending.split(",")[1]);
      const ab = new ArrayBuffer(byteString.length);
      const ia = new Uint8Array(ab);
      for (let i = 0; i < byteString.length; i++) ia[i] = byteString.charCodeAt(i);
      const blob = new Blob([ab], { type: "image/jpeg" });
      const file = new File([blob], "upload.jpg", { type: "image/jpeg" });
      setImagePreview(pending);
      setImageFile(file);
    }
  }, []);
  reactExports.useEffect(() => {
    if (!user) return;
    supabase.from("outfit_analyses").select("id,image_url,overall_style,style_score,summary,detected_items,color_palette,strengths,created_at").eq("user_id", user.id).order("created_at", { ascending: false }).then(({ data: d }) => setHistory(d || []));
  }, [user]);
  const handleFile = (f) => {
    if (!f) return;
    setImagePreview(URL.createObjectURL(f));
    setImageFile(f);
    setData(null);
    setSavedId(null);
  };
  const compressImage = (file, maxDim = 1024, quality = 0.7) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      let { width, height } = img;
      if (width > maxDim || height > maxDim) {
        if (width > height) {
          height = Math.round(height * maxDim / width);
          width = maxDim;
        } else {
          width = Math.round(width * maxDim / height);
          height = maxDim;
        }
      }
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, width, height);
      resolve(canvas.toDataURL("image/jpeg", quality).split(",")[1]);
    };
    img.onerror = () => reject(new Error("Failed to load image"));
    img.src = URL.createObjectURL(file);
  });
  const analyzeOutfit = async (file) => {
    setAnalysisFailed(false);
    setLoading(true);
    try {
      const b64 = await compressImage(file);
      const apiUrl = "https://luxor.ly";
      let fnData = null;
      for (let attempt = 0; attempt < 3; attempt++) {
        if (attempt > 0) {
          await new Promise((r) => setTimeout(r, 2e3 * attempt));
        }
        const controller = new AbortController();
        const abortTimer = setTimeout(() => controller.abort(), 12e4);
        try {
          const response = await fetch(apiUrl + "/api/v1/analyze-outfit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image_b64: b64 }),
            signal: controller.signal
          });
          clearTimeout(abortTimer);
          if (!response.ok) throw new Error("Server returned " + response.status);
          fnData = await response.json();
          if (!fnData || !fnData.success) throw new Error("Analysis failed");
          if (fnData.source === "cipher_vision") break;
        } catch (fetchErr) {
          clearTimeout(abortTimer);
          if (fetchErr.name === "AbortError") {
            throw new Error("Request timed out after 60s");
          }
          throw fetchErr;
        }
      }
      if (!fnData || fnData.source !== "cipher_vision") {
        setData(null);
        setAnalysisFailed(true);
        toast.error("Analysis timed out. Tap Retry to try again.");
        return;
      }
      const o = {
        style_name: fnData.style_name || "",
        actual_colors: fnData.actual_colors || [],
        items_detected: fnData.items_detected || [],
        strengths: fnData.strengths || [],
        audit: fnData.audit || "",
        tweak_plan: fnData.tweak_plan || "",
        generation_prompt: fnData.generation_prompt || "",
        style_score: fnData.style_score || 0,
        seasonalFit: fnData.seasonalFit || ""
      };
      setData(o);
      setSavedId(null);
      toast.success("Outfit analyzed! ✨");
    } catch (e) {
      toast.error(e.message || "Analysis failed");
      if (e.message && e.message.includes("Cipher Vision") && file) {
        const retryFile = file;
        setTimeout(() => {
          toast(
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Click to retry analysis" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "sm", variant: "outline", onClick: () => analyzeOutfit(retryFile), children: "Retry" })
            ] }),
            { duration: 8e3 }
          );
        }, 500);
      }
    } finally {
      setLoading(false);
    }
  };
  const handleSave = async () => {
    if (!data || !user || !imagePreview) return;
    setSaving(true);
    try {
      let publicUrl = imagePreview;
      if (imageFile) {
        const ext = imageFile.name.split(".").pop();
        const path = `${user.id}/${Date.now()}.${ext}`;
        const { error: upErr } = await supabase.storage.from("clothing-photos").upload(path, imageFile);
        if (!upErr) {
          const { data: pub } = supabase.storage.from("clothing-photos").getPublicUrl(path);
          publicUrl = pub.publicUrl;
        }
      }
      const { data: ins, error } = await supabase.from("outfit_analyses").insert({
        user_id: user.id,
        image_url: publicUrl,
        overall_style: data.style_name,
        style_score: data.style_score || 0,
        summary: data.audit,
        detected_items: data.items_detected.map((n) => ({ name: n, category: "Item", color: "N/A", style: "N/A" })),
        color_palette: { colors: data.actual_colors, harmony: "Balanced", rating: "Good" },
        strengths: data.strengths,
        improvements: [{ suggestion: data.tweak_plan, reason: "AI suggestion", priority: "medium" }],
        seasonal_fit: data.seasonalFit || "",
        body_type_notes: ""
      }).select("id").single();
      if (error) throw error;
      setSavedId(ins.id);
      toast.success("Analysis saved!");
    } catch (e) {
      toast.error(e.message || "Save failed");
    } finally {
      setSaving(false);
    }
  };
  const loadSaved = (s) => {
    var _a;
    setImagePreview(s.image_url);
    setImageFile(null);
    setData({
      style_name: s.overall_style || "",
      actual_colors: ((_a = s.color_palette) == null ? void 0 : _a.colors) || [],
      items_detected: (s.detected_items || []).map((i) => i.name || ""),
      strengths: s.strengths || [],
      audit: s.summary || "",
      tweak_plan: "",
      generation_prompt: "",
      style_score: s.style_score || 0
    });
    setSavedId(s.id);
  };
  const timeAgo = (d) => {
    const m = Math.floor((Date.now() - new Date(d).getTime()) / 6e4);
    return m < 60 ? `${m}m ago` : `${Math.floor(m / 60)}h ago`;
  };
  const containerVariants = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } };
  const childVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: "easeOut" } }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx(AppLayout, { children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4 md:p-8 mx-auto max-w-7xl space-y-8 overflow-x-hidden", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.div, { initial: { opacity: 0, y: -10 }, animate: { opacity: 1, y: 0 }, className: "relative", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute -top-4 -left-4 w-32 h-32 bg-primary/10 rounded-full blur-[60px]" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("h1", { className: "font-display text-4xl font-bold text-foreground relative", children: [
        "See What the World ",
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "gold-text", children: "Sees" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground mt-2 text-lg", children: "Upload your outfit. The AI scores it, finds the strengths, and tells you exactly what to fix." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-12 gap-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        motion.div,
        {
          initial: { opacity: 0, x: -20 },
          animate: { opacity: 1, x: 0 },
          className: "lg:col-span-5 relative",
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative rounded-[1.5rem] border-[0.75px] border-border p-3 sticky top-24", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(GlowingEffect, { spread: 40, glow: true, proximity: 56, inactiveZone: 0.01, borderWidth: 3 }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { className: "glass-card border-0 shadow-none overflow-hidden", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(CardContent, { className: "p-0", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(
                "div",
                {
                  onClick: () => {
                    var _a;
                    return (_a = fileRef.current) == null ? void 0 : _a.click();
                  },
                  className: "relative aspect-[3/4] cursor-pointer overflow-hidden bg-muted/20 group",
                  children: [
                    imagePreview ? /* @__PURE__ */ jsxRuntimeExports.jsx("img", { src: imagePreview, alt: "Outfit", className: "w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "absolute inset-0 flex flex-col items-center justify-center gap-3 text-muted-foreground", children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(
                        motion.div,
                        {
                          animate: { y: [0, -6, 0] },
                          transition: { duration: 2.5, repeat: Infinity },
                          className: "w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center",
                          children: /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "w-10 h-10 text-primary" })
                        }
                      ),
                      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-display text-sm", children: "Tap to upload your outfit" }),
                      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px]", children: "JPG or PNG, max 10 MB" })
                    ] }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx(
                      "input",
                      {
                        ref: fileRef,
                        type: "file",
                        accept: "image/*",
                        className: "hidden",
                        onChange: (e) => {
                          var _a;
                          const f = (_a = e.target.files) == null ? void 0 : _a[0];
                          if (f) handleFile(f);
                        }
                      }
                    )
                  ]
                }
              ),
              /* @__PURE__ */ jsxRuntimeExports.jsx(AnimatePresence, { children: loading && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                motion.div,
                {
                  initial: { opacity: 0 },
                  animate: { opacity: 1 },
                  exit: { opacity: 0 },
                  className: "absolute inset-0 bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center gap-3 z-10",
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "h-8 w-8 animate-spin text-primary" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-display text-sm", children: "Analyzing your outfit…" })
                  ]
                }
              ) })
            ] }) })
          ] })
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        motion.div,
        {
          className: "lg:col-span-7 space-y-6",
          variants: containerVariants,
          initial: "hidden",
          animate: "show",
          children: [
            data ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: childVariants, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative rounded-[1.5rem] border-[0.75px] border-border p-3", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(GlowingEffect, { spread: 60, glow: true, proximity: 80, inactiveZone: 0.01, borderWidth: 3 }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { className: "glass-card border-0 shadow-none", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(CardContent, { className: "p-6 flex flex-col md:flex-row items-center gap-6", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(CircularScore, { score: data.style_score || null }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 text-center md:text-left", children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "font-display text-2xl font-bold gold-text", children: data.style_name }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground mt-2 text-sm leading-relaxed", children: data.audit }),
                    data.seasonalFit && /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { className: "mt-2 gold-gradient text-primary-foreground", children: data.seasonalFit })
                  ] })
                ] }) })
              ] }) }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: childVariants, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative rounded-[1.5rem] border-[0.75px] border-border p-3", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(GlowingEffect, { spread: 50, glow: true, proximity: 64, inactiveZone: 0.01, borderWidth: 3 }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "glass-card border-0 shadow-none", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs(CardHeader, { className: "pb-3", children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsxs(CardTitle, { className: "font-display flex items-center gap-2 text-lg", children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-0.5 h-5 gold-gradient rounded-full mr-1" }),
                      /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-5 h-5 text-purple-400" }),
                      " Cosmic Advice & Style Diagrams"
                    ] }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "AI-powered recommendations to elevate your look." })
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs(CardContent, { className: "space-y-5", children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsxs(
                      motion.div,
                      {
                        variants: container,
                        initial: "hidden",
                        animate: "show",
                        className: "space-y-3",
                        children: [
                          /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.div, { variants: itemAnim, className: "relative", children: [
                            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute left-3 top-0 bottom-0 w-px bg-gradient-to-b from-primary/40 via-primary/20 to-transparent" }),
                            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "ml-8 pl-4 py-3 rounded-xl bg-muted/20 border border-border/40", children: [
                              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-1", children: [
                                /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs font-bold text-muted-foreground uppercase tracking-wider", children: "Current Look" }),
                                /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: "outline", className: "text-[10px] bg-primary/5", children: (data == null ? void 0 : data.style_name) || "Your Style" })
                              ] }),
                              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-foreground/80", children: (data == null ? void 0 : data.audit) || "Upload a photo to get style advice." })
                            ] })
                          ] }),
                          /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: itemAnim, className: "flex justify-center py-1", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-xs font-semibold text-primary", children: [
                            /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-3 h-3" }),
                            " Apply This Tweak"
                          ] }) }),
                          /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: itemAnim, className: "relative", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "ml-8 pl-4 py-3 rounded-xl bg-purple-500/10 border border-purple-500/20", children: [
                            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 mb-1", children: [
                              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs font-bold text-purple-400 uppercase tracking-wider", children: "Recommended Upgrade" }),
                              /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: "outline", className: "text-[10px] bg-purple-500/10 text-purple-400 border-purple-500/30", children: "AI Suggestion" })
                            ] }),
                            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-foreground/80", children: (data == null ? void 0 : data.tweak_plan) || "Complete the analysis to see a personalized upgrade." })
                          ] }) })
                        ]
                      }
                    ),
                    (data == null ? void 0 : data.items_detected) && data.items_detected.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                      motion.div,
                      {
                        variants: container,
                        initial: "hidden",
                        animate: "show",
                        className: "pt-2 border-t border-border/30",
                        children: [
                          /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.p, { variants: itemAnim, className: "text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-1.5", children: [
                            /* @__PURE__ */ jsxRuntimeExports.jsx(Eye, { className: "w-3 h-3" }),
                            " Items Detected"
                          ] }),
                          /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: itemAnim, className: "flex flex-wrap gap-2", children: data.actual_colors && data.actual_colors.length > 0 ? data.items_detected.map((item, idx) => {
                            const colorMap = {
                              "Pink": "bg-pink-500",
                              "Red": "bg-red-500",
                              "Blue": "bg-blue-500",
                              "Black": "bg-gray-900",
                              "White": "bg-white border border-border",
                              "Cream": "bg-yellow-100",
                              "Green": "bg-green-500",
                              "Brown": "bg-amber-800",
                              "Gold": "bg-yellow-500",
                              "Silver": "bg-gray-300",
                              "Navy": "bg-blue-900",
                              "Tan": "bg-amber-200",
                              "Beige": "bg-amber-100",
                              "Yellow": "bg-yellow-400",
                              "Grey": "bg-gray-400",
                              "Orange": "bg-orange-500"
                            };
                            const colorName = data.actual_colors[idx] || "";
                            const dotClass = colorName ? colorMap[colorName] || "bg-gray-400" : "bg-gray-400";
                            return /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { variant: "outline", className: "text-xs border-primary/30 bg-primary/5 backdrop-blur-sm flex items-center gap-1.5", children: [
                              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "w-2 h-2 rounded-full inline-block " + dotClass }),
                              item
                            ] }, idx);
                          }) : data.items_detected.map((item, idx) => /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: "outline", className: "text-xs border-primary/30 bg-primary/5 backdrop-blur-sm", children: item }, idx)) })
                        ]
                      }
                    ),
                    (data == null ? void 0 : data.actual_colors) && data.actual_colors.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                      motion.div,
                      {
                        variants: container,
                        initial: "hidden",
                        animate: "show",
                        className: "pt-2 border-t border-border/30",
                        children: [
                          /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.p, { variants: itemAnim, className: "text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-1.5", children: [
                            /* @__PURE__ */ jsxRuntimeExports.jsx(Palette, { className: "w-3 h-3" }),
                            " Color Palette Detected"
                          ] }),
                          /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: itemAnim, className: "flex flex-wrap gap-2", children: data.actual_colors.map((color, idx) => {
                            const colorMap = {
                              "Pink": "bg-pink-500",
                              "Red": "bg-red-500",
                              "Blue": "bg-blue-500",
                              "Black": "bg-gray-900",
                              "White": "bg-white border border-border",
                              "Cream": "bg-yellow-100",
                              "Green": "bg-green-500",
                              "Brown": "bg-amber-800",
                              "Gold": "bg-yellow-500",
                              "Silver": "bg-gray-300",
                              "Navy": "bg-blue-900",
                              "Tan": "bg-amber-200",
                              "Beige": "bg-amber-100",
                              "Yellow": "bg-yellow-400",
                              "Grey": "bg-gray-400",
                              "Orange": "bg-orange-500"
                            };
                            const bgClass = colorMap[color] || "bg-muted";
                            return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5 px-2 py-1 rounded-lg bg-muted/20 border border-border/40", children: [
                              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: `w-3 h-3 rounded-full ${bgClass}` }),
                              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs text-foreground/70", children: color })
                            ] }, idx);
                          }) })
                        ]
                      }
                    ),
                    (data == null ? void 0 : data.strengths) && data.strengths.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                      motion.div,
                      {
                        variants: container,
                        initial: "hidden",
                        animate: "show",
                        className: "pt-2 border-t border-border/30",
                        children: [
                          /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.p, { variants: itemAnim, className: "text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-1.5", children: [
                            /* @__PURE__ */ jsxRuntimeExports.jsx(ShieldCheck, { className: "w-3 h-3" }),
                            " Style Strengths"
                          ] }),
                          /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: itemAnim, className: "space-y-2", children: data.strengths.map((s, idx) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start gap-2", children: [
                            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-5 h-5 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center flex-shrink-0 mt-0.5", children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-1.5 h-1.5 rounded-full bg-green-500" }) }),
                            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-foreground/70", children: s })
                          ] }, idx)) })
                        ]
                      }
                    )
                  ] })
                ] })
              ] }) }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(InteractiveStylistQuiz, { imagePreview, styleName: data == null ? void 0 : data.style_name, actualColors: data == null ? void 0 : data.actual_colors }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(motion.div, { variants: childVariants, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative rounded-[1.5rem] border-[0.75px] border-border p-3", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent blur-2xl pointer-events-none" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(GlowingEffect, { spread: 60, glow: true, proximity: 64, inactiveZone: 0.01, borderWidth: 3 }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "glass-card border-0 shadow-none relative overflow-hidden", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute -top-10 -right-10 w-40 h-40 bg-primary/5 rounded-full blur-[80px]" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx(CardHeader, { className: "pb-2", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(CardTitle, { className: "font-display flex items-center gap-2 text-lg", children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-0.5 h-5 gold-gradient rounded-full mr-1" }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx(TrendingUp, { className: "w-5 h-5 text-primary" }),
                    " Cosmic Audit"
                  ] }) }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs(CardContent, { className: "space-y-4", children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm text-foreground leading-relaxed italic border-l-2 border-primary/30 pl-4 py-2 bg-primary/5 rounded-r-xl", children: [
                      "“",
                      data.audit,
                      "”"
                    ] }),
                    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap gap-3", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { variant: "outline", className: "text-xs bg-muted/30", children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-3 h-3 mr-1 text-primary" }),
                      " ",
                      data.tweak_plan
                    ] }) })
                  ] })
                ] })
              ] }) }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.div, { variants: childVariants, className: "flex items-center gap-3 justify-end", children: [
                !savedId ? /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { onClick: handleSave, disabled: saving, variant: "outline", className: "border-primary/30 hover:bg-primary/10", whileTap: { scale: 0.95 }, children: [
                  saving ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 mr-2 animate-spin" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-4 h-4 mr-2" }),
                  "Save Analysis"
                ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { className: "bg-green-500/15 text-green-500 border-green-500/30", children: "✓ Saved to Dressing Room" }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(
                  Button,
                  {
                    onClick: () => navigate("/dressing-room"),
                    variant: "outline",
                    className: "border-primary/30 hover:bg-primary/10",
                    whileTap: { scale: 0.95 },
                    children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-4 h-4 mr-2" }),
                      " Open Dressing Room"
                    ]
                  }
                )
              ] })
            ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx(jsxRuntimeExports.Fragment, { children: analysisFailed && imagePreview ? /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.div, { variants: childVariants, className: "text-center py-12", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "h-16 w-16 text-amber-500/70 mx-auto mb-4" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "font-display text-xl text-foreground mb-2", children: "Analysis timed out" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground text-sm max-w-sm mx-auto mb-6", children: "The AI took too long to respond. You can retry with a longer timeout, or upload a different photo." }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-center gap-3", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { onClick: () => {
                  if (imageFile) analyzeOutfit(imageFile);
                }, disabled: loading, variant: "default", className: "gap-2", children: [
                  loading ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 animate-spin" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "w-4 h-4" }),
                  loading ? "Analyzing..." : "🔄 Retry Analysis"
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { onClick: () => {
                  setImagePreview(null);
                  setImageFile(null);
                  setAnalysisFailed(false);
                }, variant: "outline", className: "gap-2", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Upload, { className: "w-4 h-4" }),
                  " Upload new photo"
                ] })
              ] })
            ] }) : (
              /* ---- Empty state ---- */
              /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.div, { variants: childVariants, className: "text-center py-12", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "h-16 w-16 text-muted-foreground mx-auto mb-4" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "font-display text-xl text-foreground mb-2", children: "Upload an outfit to begin" }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground text-sm max-w-sm mx-auto", children: "Tap the camera area on the left to upload a photo. The AI will analyze your style, colors, and fit." })
              ] })
            ) }),
            history.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(motion.div, { variants: childVariants, className: "pt-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("h3", { className: "font-display text-lg text-foreground mb-4 flex items-center gap-2", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Layers, { className: "w-5 h-5 text-primary" }),
                " Previous Analyses"
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-2 sm:grid-cols-3 gap-3", children: history.slice(0, 6).map((h) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
                motion.button,
                {
                  whileHover: { scale: 1.03, y: -2 },
                  whileTap: { scale: 0.95 },
                  onClick: () => loadSaved(h),
                  className: "relative rounded-xl overflow-hidden border border-border/50 group text-left",
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "aspect-[3/4] bg-muted/20", children: /* @__PURE__ */ jsxRuntimeExports.jsx("img", { src: h.image_url, alt: "", className: "w-full h-full object-cover", loading: "lazy" }) }),
                    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "absolute bottom-0 inset-x-0 p-2 bg-gradient-to-t from-background/90 to-transparent", children: [
                      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] font-semibold text-foreground truncate", children: h.overall_style }),
                      /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-[8px] text-muted-foreground", children: [
                        h.style_score,
                        "/100 · ",
                        timeAgo(h.created_at)
                      ] })
                    ] })
                  ]
                },
                h.id
              )) })
            ] })
          ]
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Footer, {})
  ] }) });
}
export {
  Analysis as default
};
