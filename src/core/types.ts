export interface SlideItem {
  index: number;
  imagePath: string;
  audioPath?: string;
}

export interface Manifest {
  slides: string[];
  audio: string[];
  scenes: string[];
}
