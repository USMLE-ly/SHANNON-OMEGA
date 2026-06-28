"use client";

import React, { useEffect, useRef, useState } from "react";

interface AnimatedGradientProps {
  colors?: string[];
  speed?: number;
  blur?: "light" | "medium" | "heavy";
  className?: string;
}

export function AnimatedGradient({
  colors = ["#7c3aed", "#3b82f6", "#06b6d4"],
  speed = 0.08,
  blur = "medium",
  className = "",
}: AnimatedGradientProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [loaded, setLoaded] = useState(false);
  const animationRef = useRef<number>(0);
  const timeRef = useRef<number>(0);

  const blurMap = { light: "40px", medium: "80px", heavy: "120px" };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resize();
    window.addEventListener("resize", resize);
    setLoaded(true);

    const animate = (timestamp: number) => {
      timeRef.current = timestamp * speed * 0.001;
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      ctx.clearRect(0, 0, w, h);

      const cx = w / 2;
      const cy = h / 2;
      const maxR = Math.sqrt(w * w + h * h) / 2;

      // Draw animated gradient circles
      colors.forEach((color, i) => {
        const angle = timeRef.current + (i * Math.PI * 2) / colors.length;
        const ox = Math.cos(angle) * w * 0.2;
        const oy = Math.sin(angle) * h * 0.2;
        const grad = ctx.createRadialGradient(
          cx + ox, cy + oy, 0,
          cx + ox, cy + oy, maxR
        );
        grad.addColorStop(0, color);
        grad.addColorStop(0.5, color + "80");
        grad.addColorStop(1, "transparent");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);
      });

      animationRef.current = requestAnimationFrame(animate);
    };
    animationRef.current = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationRef.current);
      window.removeEventListener("resize", resize);
    };
  }, [colors, speed]);

  return (
    <div className={`absolute inset-0 overflow-hidden ${className}`}>
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{
          filter: `blur(${blurMap[blur]})`,
          opacity: loaded ? 1 : 0,
          transition: "opacity 0.5s ease",
        }}
      />
    </div>
  );
}
