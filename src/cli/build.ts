import { runPipeline } from "../core/pipeline";

async function main() {
  console.log("Starting build pipeline...");
  await runPipeline();
  console.log("Build complete.");
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
