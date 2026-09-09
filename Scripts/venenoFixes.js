/* Veneno Tattoo — fixes for widgets that depended on Duda's own runtime
   (which no longer initializes outside Duda's hosting). Loaded after
   Duda's own bundles so it can patch behavior without editing them. */
(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    /* ---- 1) Menu links: stop Duda's own click handler (its SPA router
       never finishes booting off Duda's hosting, so it silently eats the
       click). Runs in the CAPTURE phase, before Duda's handler, so the
       native <a href> navigation goes through untouched. ---- */
    document
      .querySelectorAll('[data-element-type="onelinksmenu"] a[href], nav a[href]')
      .forEach(function (link) {
        link.addEventListener(
          'click',
          function (e) {
            e.stopImmediatePropagation();
          },
          true
        );
      });

    /* ---- 2) Auto-advance every Duda "ssrimageslider" widget that has
       more than one slide, since Duda's own JS never gets far enough to
       animate them itself. Simple show/hide on a timer — no layout
       changes, so it won't fight the widget's existing CSS. ---- */
    document.querySelectorAll('[data-widget-type="ssrimageslider"]').forEach(function (widget) {
      var slides = Array.from(widget.querySelectorAll('[data-auto^="slideSlot"]'));
      if (slides.length < 2) return;

      var current = slides.findIndex(function (s) {
        return s.classList.contains('d-ext-mediaSlider-slidesContainer__slide--active');
      });
      if (current === -1) current = 0;

      slides.forEach(function (s, i) {
        s.style.display = i === current ? '' : 'none';
      });

      setInterval(function () {
        slides[current].style.display = 'none';
        current = (current + 1) % slides.length;
        slides[current].style.display = '';
      }, 5000);
    });
  });
})();
