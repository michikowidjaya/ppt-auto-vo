import path from "node:path";
import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";

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

const escapePath = (value: string): string => value.replace(/'/g, "'\\''");

export const concatScenes = async (
  scenePaths: string[],
  outPath: string,
  ffmpegPath = "ffmpeg"
): Promise<void> => {
  await mkdir(path.dirname(outPath), { recursive: true });

  const listPath = path.join(path.dirname(outPath), "concat_list.txt");
  const lines = scenePaths.map((scene) => `file '${escapePath(scene)}'`).join("\n");
  await writeFile(listPath, lines, "utf8");

  await run(ffmpegPath, [
    "-y",
    "-f",
    "concat",
    "-safe",
    "0",
    "-i",
    listPath,
    "-c",
    "copy",
    outPath
  ]);
};
