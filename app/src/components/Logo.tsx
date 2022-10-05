type TailwindSize =
  | "sm"
  | "base"
  | "lg"
  | "xl"
  | "2xl"
  | "3xl"
  | "4xl"
  | "5xl"
  | "6xl"
  | "7xl"
  | "8xl"
  | "9xl";

interface LogoProps {
  animated?: boolean;
  size?: TailwindSize;
}

export default function JFRRS({ animated = false, size = "base" }: LogoProps) {
  let jClass = "inline-block font-jeff scale-75";
  if (animated)
    jClass = jClass.concat(
      " group-hover:-rotate-6 group-hover:scale-100 group-hover:text-fuchsia-600 transition-all"
    );
  return (
    <span className={`text-${size} tracking-wide group`}>
      <span className={jClass}>J</span>
      FRRS
    </span>
  );
}
