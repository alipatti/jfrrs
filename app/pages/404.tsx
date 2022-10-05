import Link from "next/link";
import Layout from "../components/Layout";

// TODO: add funny photo to page

export default function FourOhFour() {
  return (
    <Layout>
      <div className="text-center">
      <h1 className="mt-32 mb-5 text-2xl">404 – Page not found</h1>
      <Link href={"/"}>
        <a>Go home</a>
      </Link>
      </div>
    </Layout>
  );
}
