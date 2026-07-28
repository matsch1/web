document.querySelectorAll("[data-content-filters]").forEach((filters) => {
  const buttons = filters.querySelectorAll("[data-filter]");
  const entries = document.querySelectorAll(".post-entry[data-category]");
  const emptyState = filters.nextElementSibling;

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const category = button.dataset.filter;
      let visibleEntries = 0;

      entries.forEach((entry) => {
        const visible = category === "all" || entry.dataset.category === category;
        entry.hidden = !visible;
        visibleEntries += Number(visible);
      });

      buttons.forEach((item) => {
        const active = item === button;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", String(active));
      });
      emptyState.hidden = visibleEntries > 0;
    });
  });
});
