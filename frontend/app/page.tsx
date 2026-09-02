import { BackendStatus } from "@/components/layout/backend-status";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { Hero } from "@/components/landing/hero";
import { RepoInput } from "@/components/landing/repo-input";
import { RecentRepos } from "@/components/landing/recent-repos";

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main className="flex flex-1 flex-col justify-center">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-24">
          <Hero />
          <div className="flex max-w-md flex-col gap-6">
            <RepoInput />
            <RecentRepos />
          </div>
          <BackendStatus />
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
