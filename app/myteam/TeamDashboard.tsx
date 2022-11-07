"use client";

import {
  FantasyTeam,
  AthleteOnFantasyTeam,
  Athlete,
  FantasyLeague,
} from "@prisma/client";

export type Team =
  | (FantasyTeam & {
      athletes: (AthleteOnFantasyTeam & { athlete: Athlete })[];
      league: FantasyLeague;
    })
  | null
  | undefined;

export default function TeamDashboard({ team }: { team: Team }) {

  if (!team) return <>No team</>

  team

  return <div></div>;
}
