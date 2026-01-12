import "dotenv/config";
import path from "node:path";
import { runBuild } from "../core/pipeline.js";
import { log } from "../core/logger.js";
import type { BuildConfig } from "../core/types.js";

const mustEnv = (key: string): string => {
  const value = process.env[key];
  if (!value || value.trim().length === 0) {
    throw new Error(`Missing env ${key}`);
  }
  return value;
};

const optionalEnv = (key: string): string | undefined => {
  const value = process.env[key];
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : undefined;
};

const root = process.cwd();
const inputDir = path.join(root, "input");
const outputDir = path.join(root, "output");
const cacheDir = path.join(root, "cache");

const cfg: BuildConfig = {
  inputDir,
  outputDir,
  cacheDir,
  pptxPath: path.join(inputDir, "slides.pptx"),
  instruksiPath: path.join(inputDir, "INSTRUKSI.txt"),
  backgroundPath: optionalEnv("BACKGROUND_PATH"),
  sofficePath: optionalEnv("SOFFICE_PATH"),
  pdftoppmPath: optionalEnv("PDFTOPPM_PATH"),
  ffmpegPath: optionalEnv("FFMPEG_PATH"),
  ffprobePath: optionalEnv("FFPROBE_PATH"),
  elevenApiKey: mustEnv("ELEVENLABS_API_KEY"),
  elevenVoiceId: mustEnv("ELEVENLABS_VOICE_ID"),
  width: 1920,
  height: 1080,
  fps: 30
};

const main = async () => {
  await runBuild(cfg);
};

main().catch((err) => {
  log.error(err);
  process.exitCode = 1;
});
