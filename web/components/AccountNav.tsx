import Link from "next/link";
import { getReader } from "@/lib/auth";
import { logOut } from "@/lib/actions";

const link = "py-2.5 text-sm font-medium text-accent hover:text-accent-strong";

/** Log in / sign up links, or the reader's name, saved stories and log out. Reads the session. */
export async function AccountNav() {
  const reader = await getReader();
  if (!reader) {
    return (
      <div className="flex items-center gap-4">
        <Link href="/login" className={link}>
          Log in
        </Link>
        <Link href="/signup" className="rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white hover:bg-accent-strong">
          Sign up
        </Link>
      </div>
    );
  }
  return (
    <div className="flex items-center gap-4">
      <span className="text-sm text-muted">{reader.name}</span>
      <Link href="/saved" className={link}>
        Saved
      </Link>
      <form action={logOut}>
        <button type="submit" className={`${link} cursor-pointer`}>
          Log out
        </button>
      </form>
    </div>
  );
}
