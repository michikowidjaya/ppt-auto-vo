import fs from "fs";

export function parseInstruksi(path: string): string[] {
  const txt = fs.readFileSync(path, "utf8");
  return txt.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
}
