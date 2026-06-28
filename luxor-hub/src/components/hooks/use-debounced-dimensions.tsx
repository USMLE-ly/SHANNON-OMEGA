"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface Dimensions {
  width: number;
  height: number;
}

export function useDebouncedDimensions<T extends HTMLElement = HTMLDivElement>(
  delay: number = 150
): [React.RefObject<T | null>, Dimensions] {
  const ref = useRef<T | null>(null);
  const [dimensions, setDimensions] = useState<Dimensions>({ width: 0, height: 0 });
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const measure = useCallback(() => {
    if (ref.current) {
      const { width, height } = ref.current.getBoundingClientRect();
      setDimensions({ width, height });
    }
  }, []);

  useEffect(() => {
    measure();

    const handleResize = () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(measure, delay);
    };

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [measure, delay]);

  return [ref, dimensions];
}
