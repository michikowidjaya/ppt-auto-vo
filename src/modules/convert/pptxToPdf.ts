import path from "node:path";
import { spawn } from "node:child_process";
import { access, copyFile, mkdir } from "node:fs/promises";

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

export const pptxToPdf = async (
  pptxPath: string,
  outPdfPath: string,
  sofficePath = "soffice"
): Promise<void> => {
  const outDir = path.dirname(outPdfPath);
  await mkdir(outDir, { recursive: true });

  await run(sofficePath, [
    "--headless",
    "--convert-to",
    "pdf",
    "--outdir",
    outDir,
    pptxPath
  ]);

  const baseName = path.parse(pptxPath).name;
  const expectedPdf = path.join(outDir, `${baseName}.pdf`);

  try {
    await access(expectedPdf);
  } catch {
    throw new Error(`Expected PDF not found: ${expectedPdf}`);
  }

  if (path.resolve(expectedPdf) !== path.resolve(outPdfPath)) {
    await copyFile(expectedPdf, outPdfPath);
  }
};
