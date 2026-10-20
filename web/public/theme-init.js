(function () {
  try {
    var stored = localStorage.getItem("ig5k.theme");
    var prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
    document.documentElement.setAttribute("data-theme", stored || (prefersLight ? "light" : "dark"));
  } catch (error) {
    /* storage unavailable: keep the default theme */
  }
})();
