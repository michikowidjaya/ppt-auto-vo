import path from "node:path";
import { mkdir, writeFile } from "node:fs/promises";
import fetch from "node-fetch";

type TtsParams = {
  apiKey: string;
  voiceId: string;
  text: string;
  outPath: string;
};

export const ttsElevenLabsToMp3 = async ({
  apiKey,
  voiceId,
  text,
  outPath
}: TtsParams): Promise<void> => {
  const url = `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "xi-api-key": apiKey,
      "Content-Type": "application/json",
      Accept: "audio/mpeg"
    },
    body: JSON.stringify({
      text,
      model_id: "eleven_multilingual_v2",
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75
      }
    })
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`ElevenLabs error ${res.status}: ${body}`);
  }

  const arrayBuffer = await res.arrayBuffer();
  await mkdir(path.dirname(outPath), { recursive: true });
  await writeFile(outPath, Buffer.from(arrayBuffer));
};
