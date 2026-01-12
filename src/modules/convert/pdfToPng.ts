import path from "node:path";
import { spawn } from "node:child_process";
import { mkdir, readdir, rename, rm } from "node:fs/promises";

const run = (cmd: string, args: string[]): Promise<void> =>
  new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: "inherit" });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${cmd} exited with code ${code ?? "null"}`));
      }
    });
  });

type SlideFile = { name: string; index: number };

export const pdfToPng = async (
  pdfPath: string,
  outDir: string,
  pdftoppmPath = "pdftoppm"
): Promise<string[]> => {
  await mkdir(outDir, { recursive: true });

  const prefix = path.join(outDir, "slide");
  await run(pdftoppmPath, ["-png", "-r", "200", pdfPath, prefix]);

  const files = await readdir(outDir);
  const slides: SlideFile[] = files
    .map((name) => {
      const match = name.match(/^slide-(\d+)\.png$/);
      if (!match) {
        return null;
      }
      return { name, index: Number(match[1]) };
    })
    .filter((value): value is SlideFile => value !== null)
    .sort((a, b) => a.index - b.index);

  if (slides.length === 0) {
    throw new Error(`No PNG files found in ${outDir}`);
  }

  const maxIndex = Math.max(...slides.map((slide) => slide.index));
  const pad = Math.max(2, String(maxIndex).length);

  const results: string[] = [];

  for (const slide of slides) {
    const oldPath = path.join(outDir, slide.name);
    const newName = `slide-${String(slide.index).padStart(pad, "0")}.png`;
    const newPath = path.join(outDir, newName);

    if (oldPath !== newPath) {
      try {
        await rm(newPath, { force: true });
      } catch {
        // ignore
      }
      await rename(oldPath, newPath);
    }

    results.push(newPath);
  }

  return results;
};
