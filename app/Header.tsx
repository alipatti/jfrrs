"use client"

import { useSession, signIn, signOut } from "next-auth/react";
import Link from "next/link";
import Logo from "./Logo";

// // pages to display in navbar
type NavbarPage = [route: string, displayName: string];

const NAVBAR_PAGES: NavbarPage[] = [
  ["/myteam", "My team"],
  ["/howtoplay", "How to play"],
  ["/about", "About"],
];

export default function Header() {
  const { data: session, status } = useSession();

  return (
    <div>
      <nav className="w-full flex items-center bg-gray-100 text-gray-900 px-5 py-2">
        <Link href={"/"} className="mr-2">
            <Logo animated={true} />
        </Link>

        {NAVBAR_PAGES.map(([route, displayName]) => (
          <Link
            href={route}
            key={route}
            className="mx-5 hover:drop-shadow-lg hover:scale-105 transition-all"
          >
            {displayName}
          </Link>
        ))}

        {/* TODO replace signin/signout methods with links */}
        <div className="ml-auto flex gap-3 items-center">
          {session?.user?.image && (
            <img
              src={session.user.image}
              className="h-6 rounded-full shadow-md"
            />
          )}
          <button
            className="hover:drop-shadow-lg hover:scale-105 transition-all"
            onClick={(e) => {
              e.preventDefault();
              if (status !== "authenticated") signIn();
              else signOut();
            }}
          >
            {status == "authenticated" ? "Sign out" : "Sign in"}
          </button>
        </div>
      </nav>
    </div>
  );
}
