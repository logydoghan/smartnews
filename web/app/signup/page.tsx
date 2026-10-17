import type { Metadata } from "next";
import { AuthPage } from "@/components/AuthPage";

export const metadata: Metadata = { title: "Sign up" };

export default function SignupPage({ searchParams }: PageProps<"/signup">) {
  return (
    <AuthPage
      mode="signup"
      title="Create an account"
      intro="A free account lets you save stories to read later and comment on each one."
      searchParams={searchParams}
    />
  );
}
