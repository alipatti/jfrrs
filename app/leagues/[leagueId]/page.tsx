export default function LeaguePage({
  params: { leagueId },
}: {
  params: { leagueId: string };
}) {

  // TODO do some sort of auth to verify that user is part of the league

  // TODO make league standings page
  console.log(leagueId);
  return <h1>{leagueId}</h1>;
}
