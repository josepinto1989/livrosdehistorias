
const params = new URLSearchParams(window.location.search);
const bookId = params.get("book") || "cao-joaquim-submarino";

const bookElement = document.querySelector("#book");
const stage = document.querySelector("#stage");
const previousButton = document.querySelector("#previous");
const nextButton = document.querySelector("#next");
const position = document.querySelector("#position");
const progress = document.querySelector("#progress");
const siteTitle = document.querySelector("#siteTitle");
const mobileQuery = window.matchMedia("(max-width: 720px) and (orientation: portrait)");

let bookData = null;
let pages = [];
let lastIndex = 0;
let currentIndex = 0;
let direction = 1;
let pointerStart = null;
let ignoreNextClick = false;

const isMobileView = () => mobileQuery.matches;

function normalizeIndex(index) {
  const bounded = Math.max(0, Math.min(lastIndex, index));
  if (isMobileView() || bounded === 0 || bounded === lastIndex) return bounded;
  return 1 + Math.floor((bounded - 1) / 2) * 2;
}

function displayedIndices() {
  if (isMobileView() || currentIndex === 0 || currentIndex === lastIndex) return [currentIndex];
  return [currentIndex, Math.min(currentIndex + 1, lastIndex - 1)];
}

function appendText(parent, tagName, text, className) {
  const element = document.createElement(tagName);
  element.textContent = text;
  if (className) element.className = className;
  parent.appendChild(element);
  return element;
}

function makeImage(src, alt) {
  const image = document.createElement("img");
  image.src = `books/${bookId}/${src}`;
  image.alt = alt || "";
  image.decoding = "async";
  image.draggable = false;
  return image;
}

function renderPage(page, side, pageIndex) {
  const article = document.createElement("article");
  article.className = `book-page ${side}`;

  if (page.type === "cover") {
    article.classList.add("cover-page");
    article.appendChild(makeImage(page.image, page.alt));
    return article;
  }

  if (page.type === "image") {
    article.classList.add("image-page");
    article.appendChild(makeImage(page.image, page.alt));
  }

  if (["text", "ending", "sound"].includes(page.type)) {
    article.classList.add(`${page.type}-page`);
    const block = document.createElement("div");
    block.className = "story-block";

    if (page.type === "sound") appendText(block, "span", page.sound, "sound-word");
    if (page.heading) appendText(block, "h2", page.heading);
    (page.text || []).forEach((paragraph) => appendText(block, "p", paragraph));
    if (page.end) appendText(block, "p", page.end, "end-mark");
    article.appendChild(block);
  }

  if (pageIndex > 0 && pageIndex < lastIndex) {
    appendText(article, "span", String(pageIndex).padStart(2, "0"), `page-number ${side === "left" ? "left" : "right"}`);
  }
  return article;
}

function viewPosition() {
  if (isMobileView()) return { current: currentIndex + 1, total: pages.length };
  if (currentIndex === 0) return { current: 1, total: Math.ceil((pages.length + 1) / 2) };
  if (currentIndex === lastIndex) return { current: Math.ceil((pages.length + 1) / 2), total: Math.ceil((pages.length + 1) / 2) };
  return { current: 2 + Math.floor((currentIndex - 1) / 2), total: Math.ceil((pages.length + 1) / 2) };
}

function updateUrl() {
  const url = new URL(window.location.href);
  url.searchParams.set("book", bookId);
  url.hash = `pagina-${currentIndex + 1}`;
  window.history.replaceState(null, "", url);
}

function preloadAround() {
  const distance = isMobileView() ? 2 : 4;
  for (let offset = -distance; offset <= distance; offset += 1) {
    const page = pages[currentIndex + offset];
    if (page?.image) {
      const image = new Image();
      image.src = `books/${bookId}/${page.image}`;
    }
  }
}

function render() {
  currentIndex = normalizeIndex(currentIndex);
  const indices = displayedIndices();
  bookElement.replaceChildren();
  bookElement.className = `book ${indices.length === 1 ? "single" : "spread"}`;
  bookElement.style.setProperty("--entry-x", `${direction * 12}px`);

  indices.forEach((index, displayIndex) => {
    const side = indices.length === 1 ? "single-page" : displayIndex === 0 ? "left" : "right";
    bookElement.appendChild(renderPage(pages[index], side, index));
  });

  const view = viewPosition();
  position.textContent = `${view.current} / ${view.total}`;
  progress.style.width = `${view.total <= 1 ? 100 : ((view.current - 1) / (view.total - 1)) * 100}%`;
  previousButton.disabled = currentIndex === 0;
  nextButton.disabled = currentIndex === lastIndex;
  updateUrl();
  preloadAround();
}

function goNext() {
  if (currentIndex === lastIndex) return;
  direction = 1;
  if (isMobileView()) currentIndex += 1;
  else if (currentIndex === 0) currentIndex = 1;
  else if (currentIndex >= lastIndex - 2) currentIndex = lastIndex;
  else currentIndex += 2;
  render();
}

function goPrevious() {
  if (currentIndex === 0) return;
  direction = -1;
  if (isMobileView()) currentIndex -= 1;
  else if (currentIndex === lastIndex) currentIndex = Math.max(1, lastIndex - 2);
  else if (currentIndex <= 1) currentIndex = 0;
  else currentIndex -= 2;
  render();
}

previousButton.addEventListener("click", goPrevious);
nextButton.addEventListener("click", goNext);

document.addEventListener("keydown", (event) => {
  if (["ArrowRight", "PageDown", " "].includes(event.key)) { event.preventDefault(); goNext(); }
  if (["ArrowLeft", "PageUp"].includes(event.key)) { event.preventDefault(); goPrevious(); }
  if (event.key === "Home") { event.preventDefault(); direction = -1; currentIndex = 0; render(); }
  if (event.key === "End") { event.preventDefault(); direction = 1; currentIndex = lastIndex; render(); }
});

stage.addEventListener("pointerdown", (event) => {
  pointerStart = { x: event.clientX, y: event.clientY, time: Date.now() };
});
stage.addEventListener("pointerup", (event) => {
  if (!pointerStart) return;
  const deltaX = event.clientX - pointerStart.x;
  const deltaY = event.clientY - pointerStart.y;
  const elapsed = Date.now() - pointerStart.time;
  pointerStart = null;
  if (elapsed < 700 && Math.abs(deltaX) > 48 && Math.abs(deltaX) > Math.abs(deltaY) * 1.25) {
    ignoreNextClick = true;
    if (deltaX < 0) goNext(); else goPrevious();
  }
});
stage.addEventListener("pointercancel", () => { pointerStart = null; });
stage.addEventListener("click", (event) => {
  if (ignoreNextClick) { ignoreNextClick = false; return; }
  if (event.detail === 0) return;
  const bounds = stage.getBoundingClientRect();
  if (event.clientX < bounds.left + bounds.width / 2) goPrevious(); else goNext();
});
mobileQuery.addEventListener("change", () => {
  currentIndex = normalizeIndex(currentIndex);
  direction = 0;
  render();
});

async function init() {
  try {
    const response = await fetch(`books/${bookId}/book.json`);
    if (!response.ok) throw new Error("Livro não encontrado.");
    bookData = await response.json();
    pages = bookData.pages;
    lastIndex = pages.length - 1;
    siteTitle.textContent = bookData.title;
    document.title = `${bookData.title} — ${bookData.collectionTitle}`;
    if (bookData.themeColor) document.documentElement.style.setProperty("--accent", bookData.themeColor);

    const requested = window.location.hash.match(/pagina-(\d+)/);
    if (requested) currentIndex = Math.min(lastIndex, Math.max(0, Number(requested[1]) - 1));
    render();
  } catch (error) {
    bookElement.innerHTML = `<article class="book-page text-page"><div class="story-block"><h2>Ups!</h2><p>${error.message}</p><p><a href="index.html">Voltar à biblioteca</a></p></div></article>`;
  }
}
init();
