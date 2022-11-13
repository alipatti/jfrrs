import { FormEvent } from "react";

// convenience method to query an api endpoint given a form event
export async function apiFromFormEvent(event: FormEvent<HTMLFormElement>) {
  const body = Object.fromEntries(new FormData(event.currentTarget).entries());
  const endpoint = event.currentTarget.getAttribute("action")!;
  console.log(body);
  console.log(endpoint);
  const response = await fetch(endpoint, {
    method: event.currentTarget.getAttribute("method") || "get",
    body: JSON.stringify(body),
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json,text/*",
    },
  });

  return {
    ...response,
    body: await response.json()
  };
}
