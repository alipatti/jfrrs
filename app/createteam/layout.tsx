import { ReactNode } from "react";

export default function CreateTeamLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div>
      <h1>Create Team</h1>
      {children}
    </div>
  );
}
