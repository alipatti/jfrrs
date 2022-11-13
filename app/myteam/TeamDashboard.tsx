"use client";

import {
  FantasyTeam,
  AthleteOnFantasyTeam,
  Athlete,
  FantasyLeague,
} from "@prisma/client";
import Link from "next/link";

export type Team =
  | (FantasyTeam & {
      athletes: (AthleteOnFantasyTeam & { athlete: Athlete })[];
      league: FantasyLeague;
    })
  | null
  | undefined;

export default function TeamDashboard({ team }: { team: Team }) {
  if (!team)
    return (
      <div>
        <p>You don't have a team</p>
        <Link href="/createteam">
          <button>Create a team</button>
        </Link>
      </div>
    );

  return null;
}
