const book = document.querySelector(".codex-book");
const tabList = book.querySelector(".chapter-tabs");
const page = book.querySelector(".book-pages");
const home = book.querySelector("#book-home");

// Content will use this state when the blank pages are filled in.
const state = { view: "home", chapter: 1, page: 1 };
const tabs = [];

function renderNavigation() {
  for (const tab of tabs) {
    const selected = Number(tab.dataset.chapter) === state.chapter;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
  }
  page.setAttribute("aria-labelledby", `chapter-${state.chapter}`);
  page.dataset.chapter = String(state.chapter);
  page.dataset.page = String(state.page);
  page.dataset.view = state.view;
}

function selectChapter(chapter) {
  state.view = "chapter";
  state.chapter = chapter;
  state.page = 1;
  renderNavigation();
}

home.addEventListener("click", () => {
  state.view = "home";
  state.chapter = 1;
  state.page = 1;
  renderNavigation();
});

// The game disables Back on list views. It will become available when the
// website has a detail view to leave; chapter browsing does not create history.

for (let index = 0; index < 9; index += 1) {
  const chapter = index + 1;
  const tab = document.createElement("button");
  tab.type = "button";
  tab.className = "chapter-tab";
  tab.id = `chapter-${chapter}`;
  tab.dataset.chapter = String(chapter);
  tab.style.setProperty("--chapter-index", index);
  tab.setAttribute("role", "tab");
  tab.setAttribute("aria-label", `Chapter ${chapter}`);
  tab.setAttribute("aria-controls", "book-pages");

  for (const [assetState, className] of [
    ["normal", "tab-normal"],
    ["mouseOver", "tab-hover"],
    ["selected", "tab-selected"],
  ]) {
    const image = document.createElement("img");
    image.src = `./assets/gms-v102/RightTab/${index}/${assetState}/0.png`;
    image.className = className;
    image.width = assetState === "selected" ? 28 : 22;
    image.height = 31;
    image.alt = "";
    image.draggable = false;
    tab.append(image);
  }

  tab.addEventListener("click", () => selectChapter(chapter));
  tab.addEventListener("keydown", (event) => {
    let nextIndex;
    if (event.key === "ArrowDown") nextIndex = (index + 1) % tabs.length;
    else if (event.key === "ArrowUp") nextIndex = (index + tabs.length - 1) % tabs.length;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = tabs.length - 1;
    else return;
    event.preventDefault();
    selectChapter(nextIndex + 1);
    tabs[nextIndex].focus();
  });
  tabs.push(tab);
  tabList.append(tab);
}

renderNavigation();
