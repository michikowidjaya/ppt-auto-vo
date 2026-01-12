import path from "node:path";
import { spawn } from "node:child_process";
import { mkdir, access } from "node:fs/promises";
import { getAudioDurationSec } from "./ffprobe.js";

type RenderSceneParams = {
  slidePngPath: string;
  audioPath: string;
  outScenePath: string;
  width: number;
  height: number;
  fps: number;
  backgroundPath?: string;
  ffmpegPath?: string;
  ffprobePath?: string;
};

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

export const renderScene = async ({
  slidePngPath,
  audioPath,
  outScenePath,
  width,
  height,
  fps,
  backgroundPath,
  ffmpegPath = "ffmpeg",
  ffprobePath = "ffprobe"
}: RenderSceneParams): Promise<void> => {
  const duration = await getAudioDurationSec(audioPath, ffprobePath);
  await mkdir(path.dirname(outScenePath), { recursive: true });

  let args: string[];

  // Check if background exists
  const hasBackground = backgroundPath ? await fileExists(backgroundPath) : false;

  if (hasBackground && backgroundPath) {
    // Use background with overlay filter
    args = [
      "-y",
      "-loop",
      "1",
      "-i",
      backgroundPath,
      "-loop",
      "1",
      "-i",
      slidePngPath,
      "-i",
      audioPath,
      "-t",
      duration.toFixed(3),
      "-r",
      String(fps),
      "-filter_complex",
      `[1:v]scale=${width}:${height}:force_original_aspect_ratio=decrease[scaled];[0:v][scaled]overlay=(W-w)/2:(H-h)/2[outv]`,
      "-map",
      "[outv]",
      "-map",
      "2:a",
      "-c:v",
      "libx264",
      "-pix_fmt",
      "yuv420p",
      "-c:a",
      "aac",
      "-shortest",
      outScenePath
    ];
  } else {
    // Original behavior without background
    args = [
      "-y",
      "-loop",
      "1",
      "-i",
      slidePngPath,
      "-i",
      audioPath,
      "-t",
      duration.toFixed(3),
      "-r",
      String(fps),
      "-vf",
      `scale=${width}:${height}:force_original_aspect_ratio=decrease,pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2`,
      "-c:v",
      "libx264",
      "-pix_fmt",
      "yuv420p",
      "-c:a",
      "aac",
      "-shortest",
      outScenePath
    ];
  }

  await run(ffmpegPath, args);
};

const fileExists = async (filePath: string): Promise<boolean> => {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
};
