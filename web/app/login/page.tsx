import type { Metadata } from "next";
import { AuthPage } from "@/components/AuthPage";

export const metadata: Metadata = { title: "Log in" };

export default function LoginPage({ searchParams }: PageProps<"/login">) {
  return (
    <AuthPage
      mode="login"
      title="Log in"
      intro="Log in to save stories for later and join the conversation under each one."
      searchParams={searchParams}
    />
  );
}
