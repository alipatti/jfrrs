"use client";

import Link from "next/link";

export default function CreateTeamDefault({
  searchParams,
}: {
  searchParams: { league?: string };
}) {
  if (!searchParams?.league)
    return (
      <div>
        <p>All teams need to belong to a league!</p>
        {/* TODO link to how to play page */}
        <Link href="/createleague">
          <button>Create a league</button>
        </Link>
        <p>
          To join an existing league, you need an invite code or invite link
          from the league manager.
        </p>
        <form method="get" action="/createteam">
          <input type="text" placeholder="AFDKJA" name="league" />
        </form>
      </div>
    );

  // TODO verify that league exists

  // TODO verify that user doesn't already have a team

  return (
    <div>
      <h2>{searchParams.league}</h2>
      <form
        action="/api/fantasy/createTeam"
        method="post"
        className="mx-auto grid max-w-md gap-2"
        onSubmit={async (event) => {
          event.preventDefault();
          const response = await fetch("/api/fantasy/createTeam");
          console.log(response.text());
        }}
      >
        <label htmlFor="teamName">Team Name</label>
        <input type="text" name="teamName" />
        <input type="submit" value="Create Team" />
      </form>
    </div>
  );
}
