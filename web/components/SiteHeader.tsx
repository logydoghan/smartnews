import Link from "next/link";
import { Suspense } from "react";
import { AccountNav } from "@/components/AccountNav";

export function SiteHeader({ children }: { children?: React.ReactNode }) {
  return (
    <header className="border-b border-rule">
      <div className="mx-auto flex max-w-[1240px] flex-wrap items-center justify-between gap-4 px-6 py-5">
        <Link href="/" className="font-serif text-[30px] font-bold tracking-tight text-ink">
          SmartNews
        </Link>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          {children}
          {/* The account links depend on the session, so they stream in after the page. */}
          <Suspense fallback={null}>
            <AccountNav />
          </Suspense>
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-rule">
      <p className="mx-auto max-w-[1240px] px-6 py-6 text-[13px] leading-relaxed text-muted">
        Stories are gathered automatically each morning from public news sources. Each angle is a
        summary written by AI from the coverage it cites, and every claim links to its source. The
        angles describe how each side sees a story; they are not this site&apos;s opinion. Story images
        are illustrations made by AI, not photos of the events.
      </p>
    </footer>
  );
}
