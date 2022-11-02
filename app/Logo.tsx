interface LogoProps {
  animated?: boolean;
}

export default function Logo({ animated = false}: LogoProps) {
  // TODO convert to classnames conditional 
  let jClass = "inline-block font-jeff scale-75";
  if (animated)
    jClass = jClass.concat(
      " group-hover:-rotate-6 group-hover:scale-100 group-hover:text-fuchsia-600 transition-all"
    );
  return (
    <span className="tracking-wide group">
      <span className={jClass}>J</span>
      FRRS
    </span>
  );
}
