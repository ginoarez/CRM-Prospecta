import * as React from "react";

export interface ScrambleTextProps {
  /** Target text; changing it triggers the scramble animation toward the new value. */
  text: string;
  /** Duration of the scramble tween (seconds). */
  duration?: number;
  /** Speed of the scramble animation. */
  speed?: number;
  /** Characters used while scrambling. */
  scrambleChars?: string;
  className?: string;
  style?: React.CSSProperties;
}

declare const ScrambleText: React.FC<ScrambleTextProps>;
export default ScrambleText;
