import { spawn } from "node:child_process";

const runCapture = (cmd: string, args: string[]): Promise<string> =>
  new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });

    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        reject(new Error(`${cmd} exited with code ${code ?? "null"}: ${stderr}`));
      }
    });
  });

export const getAudioDurationSec = async (
  audioPath: string,
  ffprobePath = "ffprobe"
): Promise<number> => {
  const output = await runCapture(ffprobePath, [
    "-v",
    "error",
    "-show_entries",
    "format=duration",
    "-of",
    "default=noprint_wrappers=1:nokey=1",
    audioPath
  ]);

  const duration = Number(output);
  if (!Number.isFinite(duration)) {
    throw new Error(`Unable to parse duration from ffprobe: ${output}`);
  }
  return duration;
};
