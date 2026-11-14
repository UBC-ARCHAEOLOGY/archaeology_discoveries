/* Keep the static, reviewed weekly digest current without fetching or publishing data. */
(() => {
  const panel = document.getElementById('past-week-updates');
  const root = document.querySelector('.updates-panel');
  if (!panel || !root) return;
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Vancouver', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(new Date()).map(p => [p.type, p.value]));
  const end = `${parts.year}-${parts.month}-${parts.day}`;
  const startDay = new Date(`${end}T00:00:00Z`);
  startDay.setUTCDate(startDay.getUTCDate() - 6);
  const start = startDay.toISOString().slice(0, 10);
  root.querySelector('.updates-window').textContent = `统计区间 / Window: ${start} – ${end} · America/Vancouver`;
  root.querySelectorAll('.update-card').forEach(card => {
    const day = card.querySelector('.update-date time')?.dateTime;
    if (!day || day < start || day > end) card.remove();
  });
  root.querySelectorAll('.latest-updates-grid').forEach(grid => {
    grid.nextElementSibling.hidden = grid.querySelectorAll('.update-card').length > 0;
    grid.hidden = grid.querySelectorAll('.update-card').length === 0;
  });
})();
