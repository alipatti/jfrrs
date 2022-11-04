import Logo from "./Logo";
import Link from "next/link";
import { RiGithubFill } from "react-icons/ri";
import { IconType } from "react-icons";

interface FooterLink {
  href: string;
  display: string;
  icon?: IconType;
}

const FOOTER_PAGES: FooterLink[] = [
  { href: "/about", display: "About", icon: undefined },
  { href: "/donate", display: "Donate", icon: undefined },
  {
    href: "http://github.com/alipatti/jfrrs",
    display: "github",
    icon: RiGithubFill,
  },
];

export default function Footer() {
  return (
    <footer className="py-4 h-20 px-10 bg-primary-900 text-gray-50 flex justify-between items-center self-end">
      <div>
        <span>© </span>
        <Logo />
        <span> 2022</span>
      </div>
      <div className="text-xs self-end font-extralight ">
        © 2022{" "}
        <Link href="https://alipatti.com" className="hover:underline">
          Alistair Pattison
        </Link>
      </div>
      <div>
        <ul className="flex gap-10 font-light tracking-wide">
          {FOOTER_PAGES.map(({ href, display }) => (
            <Link href={href} key={display} className="hover:underline">
              {display}
            </Link>
          ))}
        </ul>
      </div>
    </footer>
  );
}
