import { logger } from "./logger";

export async function runPipeline() {
  logger.info("Pipeline started (stub)");
  // Here you would orchestrate: pptx->pdf, pdf->png, tts, render, concat
  await new Promise(r => setTimeout(r, 100));
  logger.info("Pipeline finished (stub)");
}
