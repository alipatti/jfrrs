"use client";

import { redirect, useRouter } from "next/navigation";
import { apiFromFormEvent } from "../clientUtil";

export default function CreateLeaguePage() {
  const router = useRouter();

  return (
    <form
      action="/api/fantasy/createLeague"
      method="post"
      className="flex flex-col gap-2"
      onSubmit={async (event) => {
        event.preventDefault();
        const response = await apiFromFormEvent(event);
        console.log(response.body);
        if (response.status == 200) {
          router.push(`/createteam/?team=${response.body.slug}`);
        }
      }}
    >
      <label htmlFor="name">Team Name</label>
      <input type="text" name="name" />
      <input type="submit" className="px-auto w-20" />
    </form>
  );
}
