"use client";
import { motion } from "motion/react";

interface FashionHeroProps {
  styleName?: string;
  styleScore?: number | null;
  strengths?: string[];
  itemsDetected?: string[];
  actualColors?: string[];
  audit?: string;
  tweakPlan?: string;
  imageUrl?: string;
}

export function FashionHero({
  styleName = "Your Style",
  styleScore,
  strengths = [],
  itemsDetected = [],
  actualColors = [],
  audit = "",
  tweakPlan = "",
  imageUrl,
}: FashionHeroProps) {
  const isNA = styleScore === null || styleScore === undefined || styleScore === 0;

  return (
    <div className="w-full">
      <div className="container mx-auto px-2 py-6 md:py-12">
        <div className="grid md:grid-cols-2 gap-6 relative overflow-x-hidden">
          {/* Image Side */}
          <div className="md:order-2 relative">
            <div className="absolute -z-10 w-72 h-72 rounded-full bg-purple-500/20 blur-3xl opacity-30 -top-10 -left-10" />
            {imageUrl ? (
              <img
                src={imageUrl}
                alt="Uploaded outfit"
                className="rounded-2xl shadow-2xl w-full object-cover filter brightness-105 max-h-[500px]"
              />
            ) : (
              <div className="rounded-2xl shadow-2xl w-full aspect-[3/4] bg-zinc-800/50 flex items-center justify-center text-muted-foreground">
                Upload a photo
              </div>
            )}
          </div>

          {/* Content Side */}
          <div className="md:order-1 flex flex-col justify-between">
            <div className="flex flex-col h-full justify-between gap-4">
              {/* Header with score */}
              <div className="flex items-center gap-4">
                <h1 className="text-5xl md:text-7xl font-bold text-foreground leading-tight tracking-tighter">
                  {styleName}
                </h1>
                <div className="flex-shrink-0">
                  <div className="relative w-20 h-20 md:w-24 md:h-24">
                    <svg width="100%" height="100%" viewBox="0 0 100 100" className="-rotate-90">
                      <circle cx="50" cy="50" r="42" fill="none" stroke="hsl(var(--muted))" strokeWidth="6" />
                      {!isNA && (
                        <motion.circle
                          cx="50" cy="50" r="42" fill="none"
                          stroke="url(#goldArc)" strokeWidth="6" strokeLinecap="round"
                          strokeDasharray={264}
                          initial={{ strokeDashoffset: 264 }}
                          animate={{ strokeDashoffset: 264 - (styleScore! / 100) * 264 }}
                          transition={{ duration: 1.5, ease: "easeOut" }}
                        />
                      )}
                      <defs>
                        <linearGradient id="goldArc" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#C6A55C" />
                          <stop offset="100%" stopColor="#E8D5A3" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      {isNA ? (
                        <span className="text-lg font-bold text-muted-foreground/40">N/A</span>
                      ) : (
                        <>
                          <span className="text-xl md:text-2xl font-bold gold-text">{styleScore}</span>
                          <span className="text-[8px] text-muted-foreground">/ 100</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Items detected */}
              {itemsDetected.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {itemsDetected.map((item, i) => (
                    <span key={i} className="px-3 py-1 rounded-full bg-zinc-800/60 border border-zinc-700/50 text-xs text-foreground/80">
                      {item}
                    </span>
                  ))}
                </div>
              )}

              {/* Colors */}
              {actualColors.length > 0 && (
                <div className="flex gap-2 items-center">
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Colors:</span>
                  {actualColors.map((c, i) => (
                    <span key={i} className="px-2 py-0.5 rounded-full bg-zinc-800/40 border border-zinc-700/30 text-xs text-foreground/70">{c}</span>
                  ))}
                </div>
              )}

              {/* Strengths list */}
              <ul className="space-y-2 tracking-tighter text-base text-foreground/80">
                {strengths.length > 0 ? strengths.map((item, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0.8 }}
                    whileHover={{ opacity: 1, y: -2, transition: { duration: 0.3, ease: "easeOut" } }}
                    className="flex items-center gap-2"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500/70 flex-shrink-0" />
                    {item}
                  </motion.li>
                )) : (
                  <li className="text-muted-foreground/50">No strengths detected</li>
                )}
              </ul>

              {/* Audit / Tweak */}
              <div className="space-y-3 mt-auto pt-4 border-t border-zinc-800/60">
                {audit && (
                  <p className="text-sm text-foreground/70 leading-relaxed">{audit}</p>
                )}
                {tweakPlan && (
                  <p className="text-sm text-purple-400/80 italic">
                    <span className="font-semibold text-purple-400">Tweak:</span> {tweakPlan}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
