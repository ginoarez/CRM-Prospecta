import { ComponentType, ReactNode } from "react";

export interface SpotlightCardProps {
  children?: ReactNode;
  className?: string;
  spotlightColor?: string;
}

declare const SpotlightCard: ComponentType<SpotlightCardProps>;
export default SpotlightCard;
