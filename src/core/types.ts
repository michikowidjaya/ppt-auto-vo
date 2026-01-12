export type SlideScript = {
  slideIndex: number;
  bullets: string[];
  narration: string;
};

export type BuildConfig = {
  inputDir: string;
  outputDir: string;
  cacheDir: string;
  pptxPath: string;
  instruksiPath: string;
  backgroundPath?: string;
  sofficePath?: string;
  pdftoppmPath?: string;
  ffmpegPath?: string;
  ffprobePath?: string;
  elevenApiKey: string;
  elevenVoiceId: string;
  width: number;
  height: number;
  fps: number;
};
