
async function loadLibrary() {
  const grid = document.querySelector("#bookGrid");
  try {
    const response = await fetch("books/books.json");
    if (!response.ok) throw new Error("Não foi possível carregar a biblioteca.");
    const data = await response.json();

    data.books.forEach((book) => {
      const available = book.status === "available";
      const card = document.createElement(available ? "a" : "article");
      card.className = `library-card${available ? "" : " soon"}`;
      if (available) card.href = book.href;

      const cover = document.createElement("div");
      cover.className = "card-cover";
      if (book.cover) {
        const image = document.createElement("img");
        image.src = book.cover;
        image.alt = `Capa de ${book.title}`;
        image.loading = "lazy";
        cover.appendChild(image);
      } else {
        const placeholder = document.createElement("div");
        placeholder.className = "placeholder-cover";
        placeholder.textContent = "✦";
        cover.appendChild(placeholder);
      }

      const info = document.createElement("div");
      info.className = "card-info";
      const title = document.createElement("h3");
      title.textContent = book.title;
      const subtitle = document.createElement("p");
      subtitle.textContent = book.subtitle;
      const tag = document.createElement("span");
      tag.className = "card-tag";
      tag.textContent = available ? "Ler aventura" : "Em breve";

      info.append(title, subtitle, tag);
      card.append(cover, info);
      grid.appendChild(card);
    });
  } catch (error) {
    grid.innerHTML = `<p>Não foi possível abrir a biblioteca. ${error.message}</p>`;
  }
}
loadLibrary();
