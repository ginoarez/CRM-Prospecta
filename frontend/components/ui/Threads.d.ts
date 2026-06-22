import { ComponentType, HTMLAttributes } from "react";

export interface ThreadsProps extends HTMLAttributes<HTMLDivElement> {
  /** RGB 0..1. Color of the threads. */
  color?: [number, number, number];
  amplitude?: number;
  distance?: number;
  enableMouseInteraction?: boolean;
  /** Hard cap on device pixel ratio (perf). Default 1. */
  dpr?: number;
  /** Max render framerate. Default 30. */
  fps?: number;
}

declare const Threads: ComponentType<ThreadsProps>;
export default Threads;
