import type { ReactNode } from 'react';

type PlaceholderPageProps = {
  title: string;
  description: string;
  children?: ReactNode;
};

export function PlaceholderPage({ title, description, children }: PlaceholderPageProps) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col justify-center gap-3 px-6 py-16">
      <p className="text-xs font-medium uppercase tracking-widest text-slate-400">
        Sponsorship Tracker
      </p>
      <h1 className="text-3xl font-semibold text-slate-900">{title}</h1>
      <p className="text-slate-600">{description}</p>
      {children}
    </main>
  );
}
