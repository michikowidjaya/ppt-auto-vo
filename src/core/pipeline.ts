import path from "node:path";
import { access, mkdir } from "node:fs/promises";
import { parseInstruksi } from "../modules/script/parseInstruksi.js";
import { pptxToPdf } from "../modules/convert/pptxToPdf.js";
import { pdfToPng } from "../modules/convert/pdfToPng.js";
import { ttsElevenLabsToMp3 } from "../modules/tts/elevenlabs.js";
import { renderScene } from "../modules/render/renderScene.js";
import { concatScenes } from "../modules/render/concatScenes.js";
import { log } from "./logger.js";
import type { BuildConfig, SlideScript } from "./types.js";

const fileExists = async (filePath: string): Promise<boolean> => {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
};

export const runBuild = async (cfg: BuildConfig): Promise<void> => {
  const pdfOut = path.join(cfg.cacheDir, "pdf", "slides.pdf");
  const slidesDir = path.join(cfg.cacheDir, "slides");
  const audioDir = path.join(cfg.cacheDir, "audio");
  const scenesDir = path.join(cfg.cacheDir, "scenes");
  const outMp4 = path.join(cfg.outputDir, "output.mp4");

  await mkdir(cfg.outputDir, { recursive: true });
  await mkdir(cfg.cacheDir, { recursive: true });

  log.info("Parsing INSTRUKSI...");
  const scripts = await parseInstruksi(cfg.instruksiPath);
  const scriptMap = new Map<number, SlideScript>(
    scripts.map((script) => [script.slideIndex, script])
  );

  log.info("Converting PPTX to PDF...");
  await pptxToPdf(cfg.pptxPath, pdfOut, cfg.sofficePath ?? "soffice");

  log.info("Converting PDF to PNG...");
  const slidePngs = await pdfToPng(
    pdfOut,
    slidesDir,
    cfg.pdftoppmPath ?? "pdftoppm"
  );

  const scenePaths: string[] = [];

  for (let i = 0; i < slidePngs.length; i += 1) {
    const slideIndex = i + 1;
    const slidePngPath = slidePngs[i];
    const baseName = path.parse(slidePngPath).name;
    const audioPath = path.join(audioDir, `${baseName}.mp3`);
    const scenePath = path.join(scenesDir, `${baseName}.mp4`);

    const script = scriptMap.get(slideIndex);
    const scriptNarration = script?.narration?.trim();
    const narration =
      scriptNarration && scriptNarration.length > 0
        ? scriptNarration
        : `Slide ${slideIndex}.`;

    if (!(await fileExists(audioPath))) {
      log.info(`Generating TTS for slide ${slideIndex}...`);
      await ttsElevenLabsToMp3({
        apiKey: cfg.elevenApiKey,
        voiceId: cfg.elevenVoiceId,
        text: narration,
        outPath: audioPath
      });
    }

    log.info(`Rendering scene for slide ${slideIndex}...`);
    await renderScene({
      slidePngPath,
      audioPath,
      outScenePath: scenePath,
      width: cfg.width,
      height: cfg.height,
      fps: cfg.fps,
      backgroundPath: cfg.backgroundPath,
      ffmpegPath: cfg.ffmpegPath ?? "ffmpeg",
      ffprobePath: cfg.ffprobePath ?? "ffprobe"
    });

    scenePaths.push(scenePath);
  }

  log.info("Concatenating scenes...");
  await concatScenes(scenePaths, outMp4, cfg.ffmpegPath ?? "ffmpeg");

  log.info("DONE");
};
