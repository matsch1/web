(() => {
  "use strict";

  const enhanceGalleries = () => {
    document.querySelectorAll(".image-gallery").forEach((gallery) => {
      if (gallery.querySelector(":scope > .image-gallery__hero")) return;

      const items = Array.from(gallery.children).filter((child) =>
        child.classList.contains("image-gallery__item"),
      );
      if (items.length === 0) return;

      const hero = document.createElement("div");
      hero.className = "image-gallery__hero";
      hero.append(items[0]);

      const strip = document.createElement("div");
      strip.className = "image-gallery__strip";
      items.slice(1).forEach((item) => strip.append(item));

      gallery.replaceChildren(hero);
      if (strip.childElementCount > 0) gallery.append(strip);
    });
  };

  enhanceGalleries();

  if (!window.HTMLDialogElement) {
    return;
  }

  const labels = document.documentElement.lang.startsWith("de")
    ? { close: "Galerie schließen", previous: "Vorheriges Bild", next: "Nächstes Bild" }
    : { close: "Close gallery", previous: "Previous image", next: "Next image" };

  const dialog = document.createElement("dialog");
  dialog.className = "gallery-lightbox";
  dialog.innerHTML = `
    <div class="gallery-lightbox__content" role="document">
      <button class="gallery-lightbox__close" type="button" aria-label="${labels.close}">×</button>
      <button class="gallery-lightbox__previous" type="button" aria-label="${labels.previous}">‹</button>
      <img class="gallery-lightbox__image" alt="">
      <button class="gallery-lightbox__next" type="button" aria-label="${labels.next}">›</button>
      <p class="gallery-lightbox__caption"></p>
      <p class="gallery-lightbox__position" aria-live="polite"></p>
    </div>`;
  document.body.append(dialog);

  const image = dialog.querySelector(".gallery-lightbox__image");
  const caption = dialog.querySelector(".gallery-lightbox__caption");
  const position = dialog.querySelector(".gallery-lightbox__position");
  const previous = dialog.querySelector(".gallery-lightbox__previous");
  const next = dialog.querySelector(".gallery-lightbox__next");
  const close = dialog.querySelector(".gallery-lightbox__close");

  let items = [];
  let index = 0;
  let trigger = null;

  const show = (newIndex) => {
    index = newIndex;
    const item = items[index];
    const thumbnail = item.querySelector("img");
    const figure = item.closest("figure");
    const figureCaption = figure?.querySelector("figcaption")?.textContent.trim();

    image.src = item.href;
    image.alt = thumbnail?.alt || "";
    caption.textContent = figureCaption || "";
    caption.hidden = !figureCaption;
    position.textContent = `${index + 1} / ${items.length}`;
    previous.disabled = index === 0;
    next.disabled = index === items.length - 1;
  };

  const open = (event, item) => {
    event.preventDefault();
    const gallery = item.closest(".image-gallery");
    const cover = item.closest(".post-cover-lightbox");
    items = gallery ? Array.from(gallery.querySelectorAll(".image-gallery__link")) : [cover];
    trigger = item;
    show(items.indexOf(item));
    dialog.showModal();
    close.focus();
  };

  document.addEventListener("click", (event) => {
    const galleryItem = event.target.closest(".image-gallery__link");
    const coverItem = event.target.closest(".post-cover-lightbox");
    const item = galleryItem || coverItem;
    if (item) {
      open(event, item);
    }
  });

  previous.addEventListener("click", () => {
    if (index > 0) show(index - 1);
  });
  next.addEventListener("click", () => {
    if (index < items.length - 1) show(index + 1);
  });
  close.addEventListener("click", () => dialog.close());

  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" && index > 0) {
      event.preventDefault();
      show(index - 1);
    }
    if (event.key === "ArrowRight" && index < items.length - 1) {
      event.preventDefault();
      show(index + 1);
    }
  });
  dialog.addEventListener("close", () => {
    image.removeAttribute("src");
    trigger?.focus();
    trigger = null;
  });
})();
