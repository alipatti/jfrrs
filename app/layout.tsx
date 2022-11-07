"use client"

import Header from "./Header";
import Footer from "./Footer";
import AuthContext from "./AuthContext";

import "../styles/globals.css";

interface Props {
  children: React.ReactNode;
  showHeader?: boolean;
  showFooter?: boolean;
}

export default function RootLayout({
  children,
  showHeader = true,
  showFooter = true,
}: Props) {
  return (
    <html>
      <head>
        {/* IMPROVEMENT change to `next/font` import? */}
        <link
          href="https://fonts.googleapis.com/css2?family=Karla:ital,wght@0,200;0,300;0,400;0,600;0,700;0,800;1,300;1,400;1,700&family=Rock+Salt&display=swap"
          rel="stylesheet"
        />
      </head>
      <AuthContext>
        <body className="min-h-screen grid">
          {showHeader && <Header />}
          <main className="m-5 max-w-3xl w-full mx-auto">{children}</main>
          {showFooter && <Footer />}
        </body>
      </AuthContext>
    </html>
  );
}
