import path from "node:path";
import { spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import { getAudioDurationSec } from "./ffprobe.js";

type RenderSceneParams = {
  slidePngPath: string;
  audioPath: string;
  outScenePath: string;
  width: number;
  height: number;
  fps: number;
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
  ffmpegPath = "ffmpeg",
  ffprobePath = "ffprobe"
}: RenderSceneParams): Promise<void> => {
  const duration = await getAudioDurationSec(audioPath, ffprobePath);
  await mkdir(path.dirname(outScenePath), { recursive: true });

  const args = [
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

  await run(ffmpegPath, args);
};
