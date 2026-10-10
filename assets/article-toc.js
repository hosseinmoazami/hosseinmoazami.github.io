(() => {
  const toc = document.querySelector("[data-article-toc]");
  if (!toc) return;

  const details = toc.querySelector("details");
  const nav = toc.querySelector(".article-toc-nav");
  const links = [...toc.querySelectorAll('.article-toc-list a[href^="#"]')];
  const sections = links
    .map((link) => document.getElementById(link.hash.slice(1)))
    .filter(Boolean);

  const compactLayout = window.matchMedia("(max-width: 1179px)");
  const syncDisclosure = ({ matches }) => {
    details.toggleAttribute("open", !matches);
  };

  syncDisclosure(compactLayout);
  compactLayout.addEventListener("change", syncDisclosure);

  if (!links.length || !sections.length) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let currentId = "";
  let scheduled = false;

  const updateCurrentSection = () => {
    const marker = Math.min(window.innerHeight * 0.3, 220);
    let current = sections[0];

    for (const section of sections) {
      if (section.getBoundingClientRect().top <= marker) current = section;
      else break;
    }

    if (current.id === currentId) {
      scheduled = false;
      return;
    }

    currentId = current.id;
    let activeLink;
    for (const link of links) {
      const isCurrent = link.hash === `#${currentId}`;
      if (isCurrent) {
        link.setAttribute("aria-current", "location");
        activeLink = link;
      } else {
        link.removeAttribute("aria-current");
      }
    }

    if (details.open && activeLink) {
      const linkRect = activeLink.getBoundingClientRect();
      const navRect = nav.getBoundingClientRect();

      if (linkRect.top < navRect.top || linkRect.bottom > navRect.bottom) {
        const centeredTop = nav.scrollTop
          + linkRect.top
          - navRect.top
          - (nav.clientHeight - linkRect.height) / 2;

        nav.scrollTo({
          top: Math.max(0, centeredTop),
          behavior: reducedMotion.matches ? "auto" : "smooth",
        });
      }
    }

    scheduled = false;
  };

  const scheduleUpdate = () => {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(updateCurrentSection);
  };

  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate, { passive: true });
  window.addEventListener("hashchange", scheduleUpdate);
  details.addEventListener("toggle", scheduleUpdate);
  updateCurrentSection();
})();
