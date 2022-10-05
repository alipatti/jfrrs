import { useSession, signIn, signOut } from "next-auth/react";
import Link from "next/link";
import JFRRS from "./Logo";

// pages to display in navbar
type NavbarPage = [route: string, displayName: string];
const NAVBAR_PAGES: NavbarPage[] = [
  // ["/", "Home"],
  ["/myteam", "My team"],
  ["/howtoplay", "How to play"],
];
const FOOTER_PAGES: NavbarPage[] = [
  ["/about", "About"],
  ["/donate", "Donate"],
];

interface LayoutProps {
  children?: React.ReactNode;
  title?: string;
  showNavbar?: boolean;
  showFooter?: boolean;
}

export default function Layout({
  title,
  children,
  showNavbar = true,
  showFooter = true,
}: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {showNavbar && <Navbar />}
      <main className="m-5 max-w-3xl w-full mx-auto">
        {title && <h1 className="text-4xl mb-4">{title}</h1>}
        {children}
      </main>
      {showFooter && <Footer />}
    </div>
  );
}

export function Navbar() {
  const { data: session, status } = useSession();

  return (
    <div>
      <nav className="w-full flex items-center bg-gray-100 text-gray-900 px-5 py-2">
        <Link href={"/"}>
          <a className="mr-2">
            <JFRRS size="2xl" animated={true} />
          </a>
        </Link>

        {NAVBAR_PAGES.map(([route, displayName]) => (
          <Link href={route} key={route}>
            <a className="mx-5 hover:drop-shadow-lg hover:scale-105 transition-all">
              {displayName}
            </a>
          </Link>
        ))}

        <div className="ml-auto flex gap-3 items-center">
          {session?.user?.image && <img src={session.user.image} className="h-6 rounded-full shadow-md"/>}
          <button
            // href="/api/auth/signin"
            className="hover:drop-shadow-lg hover:scale-105 transition-all"
            onClick={(e) => {
              e.preventDefault();
              if (status !== "authenticated") signIn();
              else signOut();
            }}
          >
            {status !== "authenticated" ? "Sign in" : "Sign out"}
          </button>
        </div>
      </nav>
    </div>
  );
}

export function Footer() {
  return (
    <footer className="py-4 mt-auto h-20 px-10 bg-primary-900 text-gray-50 flex justify-between items-center">
      <div>
        <span>© </span>
        <JFRRS />
        <span> 2022</span>
      </div>
      <div className="text-xs self-end font-extralight ">
        An app by{" "}
        <Link href="https://alipatti.com">
          <a className="hover:underline">Alistair Pattison</a>
        </Link>
      </div>
      <div>
        <ul className="flex gap-10 font-light tracking-wide">
          {FOOTER_PAGES.map(([route, displayName]) => (
            <Link href={route} key={route}>
              <a className="hover:underline">{displayName}</a>
            </Link>
          ))}
        </ul>
      </div>
    </footer>
  );
}
