import { readFile } from "node:fs/promises";
import type { SlideScript } from "../../core/types.js";

export const parseInstruksi = async (
  instruksiPath: string
): Promise<SlideScript[]> => {
  const content = await readFile(instruksiPath, "utf8");
  const lines = content.split(/\r?\n/);

  const slides: SlideScript[] = [];
  let current: SlideScript | null = null;

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (line.length === 0) {
      continue;
    }

    const headerMatch = line.match(/^\[SLIDE\s+(\d+)\]\s*$/i);
    if (headerMatch) {
      const slideIndex = Number(headerMatch[1]);
      current = {
        slideIndex,
        bullets: [],
        narration: ""
      };
      slides.push(current);
      continue;
    }

    const bulletMatch = line.match(/^-+\s*(.+)$/);
    if (bulletMatch && current) {
      const bullet = bulletMatch[1].trim();
      if (bullet.length > 0) {
        current.bullets.push(bullet);
      }
    }
  }

  for (const slide of slides) {
    slide.narration = slide.bullets.join(". ");
  }

  return slides;
};
