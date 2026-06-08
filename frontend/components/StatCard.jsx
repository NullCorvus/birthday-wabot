export default function StatCard({ title, value, subtitle, icon, accent = false }) {
  return (
    <div
      className={`rounded-2xl border p-5 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg
        ${
          accent
            ? "border-accent/30 bg-gradient-to-br from-accent/10 to-accent/5 dark:from-accent/15 dark:to-accent/5"
            : "border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900"
        }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            {title}
          </p>
          <p className={`mt-2 text-3xl font-bold ${accent ? "text-accent" : "text-zinc-900 dark:text-white"}`}>
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`rounded-xl p-2.5 ${accent ? "bg-accent/20 text-accent" : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400"}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
